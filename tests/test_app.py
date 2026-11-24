"""End-to-end integration tests for ComPaye Tarjetas (MVP + V2 + V3)."""

import io
import os
import tempfile
import unittest

from PIL import Image

from app import create_app
from config import Config
from models import db
from models.contenedor import Contenedor
from models.tarjeta import Tarjeta


class ComPayeTestCase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()

        class TestConfig(Config):
            TESTING = True
            DATABASE_DIR = self.tmpdir.name
            DATABASE_PATH = os.path.join(self.tmpdir.name, 'test.db')
            SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH
            UPLOAD_FOLDER = os.path.join(self.tmpdir.name, 'uploads')

        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.engine.dispose()
        self.tmpdir.cleanup()

    def _make_image_bytes(self, color=(40, 110, 160), fmt='PNG'):
        buf = io.BytesIO()
        img = Image.new('RGBA' if fmt == 'PNG' else 'RGB', (800, 600), color)
        img.save(buf, format=fmt)
        buf.seek(0)
        return buf

    def test_root_redirects_to_tarjetas(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/tarjetas', resp.headers['Location'])

    def test_containers_crud_and_delete_guard(self):
        # Create container
        r = self.client.post(
            '/contenedores/crear',
            data={'nombre': "Caja A-1 'Norte'", 'descripcion': 'Estante superior'},
            follow_redirects=True,
        )
        self.assertEqual(r.status_code, 200)
        self.assertIn("Caja A-1 &#39;Norte&#39;", r.get_data(as_text=True))

        with self.app.app_context():
            c = Contenedor.query.first()
            cid = c.id

        # Duplicate blocked
        r_dup = self.client.post(
            '/contenedores/crear',
            data={'nombre': "Caja A-1 'Norte'"},
            follow_redirects=True,
        )
        self.assertIn('Ya existe un contenedor', r_dup.get_data(as_text=True))

        # Edit container
        r_edit = self.client.post(
            f'/contenedores/{cid}/editar',
            data={'nombre': 'Caja A-1', 'descripcion': 'Pasillo 2'},
            follow_redirects=True,
        )
        self.assertIn('Caja A-1', r_edit.get_data(as_text=True))

        # Delete container
        r_del = self.client.post(f'/contenedores/{cid}/eliminar', follow_redirects=True)
        self.assertIn('eliminado', r_del.get_data(as_text=True))

    def test_card_crud_photo_validation_and_preservation(self):
        self.client.post('/contenedores/crear', data={'nombre': 'Caja B-2'})
        with self.app.app_context():
            cid = Contenedor.query.first().id

        # Create card with RGBA photo saved as JPEG (must convert safely)
        img_buf = self._make_image_bytes(fmt='PNG')
        r = self.client.post(
            '/tarjetas/nueva',
            data={
                'numero_tarjeta': 'BN41-02528A',
                'modelo_pantalla': 'Samsung UN55MU6100',
                'precio': '1250.50',
                'stock': '2',
                'contenedor_id': str(cid),
                'compatibilidades': 'UN55MU6300, UN50MU6100, un55mu6300',
                'foto': (img_buf, 'placa.png'),
            },
            content_type='multipart/form-data',
            follow_redirects=True,
        )
        self.assertEqual(r.status_code, 200)
        html = r.get_data(as_text=True)
        self.assertIn('BN41-02528A', html)
        self.assertIn('$1,250.50', html)
        self.assertIn('Bajo stock', html)

        # Duplicate numero_tarjeta preserves typed fields on error
        r_dup = self.client.post(
            '/tarjetas/nueva',
            data={
                'numero_tarjeta': 'BN41-02528A',
                'modelo_pantalla': 'LG Modelo Especial',
                'precio': '980',
                'stock': '5',
                'compatibilidades': 'LG 49UJ6300',
            },
            follow_redirects=True,
        )
        dup_html = r_dup.get_data(as_text=True)
        self.assertIn('Ya existe una tarjeta registrada', dup_html)
        self.assertIn('LG Modelo Especial', dup_html)
        self.assertIn('980', dup_html)

        # Corrupt photo rejected safely without 500
        r_bad_img = self.client.post(
            '/tarjetas/nueva',
            data={
                'numero_tarjeta': 'T-999',
                'modelo_pantalla': 'Sony Bravia',
                'precio': '500',
                'stock': '1',
                'foto': (io.BytesIO(b'not-an-image'), 'fake.jpg'),
            },
            content_type='multipart/form-data',
            follow_redirects=True,
        )
        self.assertEqual(r_bad_img.status_code, 200)
        self.assertIn('No se pudo leer la imagen', r_bad_img.get_data(as_text=True))

    def test_v2_combined_filters_sorting_and_views(self):
        self.client.post('/contenedores/crear', data={'nombre': 'Caja 1'})
        with self.app.app_context():
            c1 = Contenedor.query.first().id

        self.client.post('/tarjetas/nueva', data={
            'numero_tarjeta': 'A-100',
            'modelo_pantalla': 'Samsung 55',
            'precio': '400',
            'stock': '5',
            'contenedor_id': str(c1),
            'compatibilidades': 'Hisense 55H6G',
        }, follow_redirects=True)
        self.client.post('/tarjetas/nueva', data={
            'numero_tarjeta': 'B-200',
            'modelo_pantalla': 'LG 43',
            'precio': '1200',
            'stock': '0',
            'contenedor_id': '',
            'compatibilidades': 'LG 43LM6300',
        }, follow_redirects=True)
        self.client.post('/tarjetas/nueva', data={
            'numero_tarjeta': 'C-300',
            'modelo_pantalla': 'TCL 50',
            'precio': '750',
            'stock': '2',
            'contenedor_id': str(c1),
        }, follow_redirects=True)

        # Unassigned filter
        r_unassigned = self.client.get('/tarjetas?contenedor=sin_asignar')
        self.assertIn('B-200', r_unassigned.get_data(as_text=True))
        self.assertNotIn('A-100', r_unassigned.get_data(as_text=True))

        # Malformed contenedor param doesn't crash
        r_bad_param = self.client.get('/tarjetas?contenedor=abc')
        self.assertEqual(r_bad_param.status_code, 200)

        # Price range + table view + sort
        r_range = self.client.get('/tarjetas?precio_min=500&precio_max=1500&vista=tabla&orden=precio_asc')
        html_range = r_range.get_data(as_text=True)
        self.assertEqual(r_range.status_code, 200)
        self.assertIn('inventory-table', html_range)
        self.assertIn('C-300', html_range)
        self.assertIn('B-200', html_range)
        self.assertNotIn('A-100', html_range)

        # Compatibility search
        r_compat = self.client.get('/tarjetas?q=Hisense')
        self.assertIn('A-100', r_compat.get_data(as_text=True))
        self.assertNotIn('B-200', r_compat.get_data(as_text=True))

        # Stock state filters
        r_bajo = self.client.get('/tarjetas?stock=bajo')
        self.assertIn('C-300', r_bajo.get_data(as_text=True))
        self.assertNotIn('A-100', r_bajo.get_data(as_text=True))
        self.assertNotIn('B-200', r_bajo.get_data(as_text=True))

    def test_ajax_stock_update_and_v3_dashboard(self):
        self.client.post('/contenedores/crear', data={'nombre': 'Estante X'})
        with self.app.app_context():
            cid = Contenedor.query.first().id

        self.client.post('/tarjetas/nueva', data={
            'numero_tarjeta': 'ST-01',
            'modelo_pantalla': 'Sony 65',
            'precio': '1500',
            'stock': '1',
            'contenedor_id': str(cid),
        })
        with self.app.app_context():
            tid = Tarjeta.query.first().id

        # AJAX decrement -> 0 (agotado)
        r_dec = self.client.post(
            f'/tarjetas/{tid}/stock',
            data={'action': 'decrement'},
            headers={'X-Requested-With': 'XMLHttpRequest'},
        )
        self.assertEqual(r_dec.status_code, 200)
        payload = r_dec.get_json()
        self.assertTrue(payload['ok'])
        self.assertEqual(payload['stock'], 0)
        self.assertEqual(payload['estado'], 'agotado')

        # AJAX increment -> 1 (bajo)
        r_inc = self.client.post(
            f'/tarjetas/{tid}/stock',
            data={'action': 'increment'},
            headers={'X-Requested-With': 'XMLHttpRequest'},
        )
        self.assertEqual(r_inc.get_json()['stock'], 1)
        self.assertEqual(r_inc.get_json()['estado'], 'bajo')

        # Dashboard V3
        r_dash = self.client.get('/estadisticas')
        self.assertEqual(r_dash.status_code, 200)
        dash_html = r_dash.get_data(as_text=True)
        self.assertIn('Estadísticas del Inventario', dash_html)
        self.assertIn('$1,500.00', dash_html)
        self.assertIn('Estante X', dash_html)
        self.assertIn('ST-01', dash_html)

        # /dashboard alias redirects cleanly
        r_alias = self.client.get('/dashboard')
        self.assertEqual(r_alias.status_code, 302)
        self.assertIn('/estadisticas', r_alias.headers['Location'])

    def test_edit_delete_pagination_and_404(self):
        self.client.post('/contenedores/crear', data={'nombre': 'Cajón 1'}, follow_redirects=True)
        with self.app.app_context():
            cid = Contenedor.query.first().id

        self.client.post('/tarjetas/nueva', data={
            'numero_tarjeta': 'ED-01',
            'modelo_pantalla': 'Modelo Viejo',
            'precio': '300',
            'stock': '4',
            'contenedor_id': str(cid),
            'compatibilidades': 'P1, P2',
        }, follow_redirects=True)
        with self.app.app_context():
            tid = Tarjeta.query.first().id

        # Edit card
        r_edit = self.client.post(f'/tarjetas/{tid}/editar', data={
            'numero_tarjeta': 'ED-01',
            'modelo_pantalla': 'Modelo Actualizado',
            'precio': '450.75',
            'stock': '3',
            'contenedor_id': '',
            'compatibilidades': 'P3',
        }, follow_redirects=True)
        html_edit = r_edit.get_data(as_text=True)
        self.assertIn('Modelo Actualizado', html_edit)
        self.assertIn('$450.75', html_edit)
        self.assertIn('P3', html_edit)
        self.assertNotIn('P1', html_edit)

        # Dashboard shows unassigned card
        r_dash = self.client.get('/estadisticas')
        self.assertIn('Sin contenedor asignado', r_dash.get_data(as_text=True))

        # Delete card
        r_del = self.client.post(f'/tarjetas/{tid}/eliminar', follow_redirects=True)
        self.assertIn('eliminada del inventario', r_del.get_data(as_text=True))

        # 404 friendly page
        r_404 = self.client.get('/tarjetas/99999')
        self.assertEqual(r_404.status_code, 404)
        self.assertIn('Página no encontrada', r_404.get_data(as_text=True))


if __name__ == '__main__':
    unittest.main()
