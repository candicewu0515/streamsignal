import unittest, importlib.util, pathlib, tempfile, threading, urllib.request, urllib.error, json
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('local_server',ROOT/'tools/serve.py');server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)
class ExportServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();server.ROOT=pathlib.Path(cls.temp.name)
        class QuietHandler(server.Handler):
            def log_message(self,*args):pass
        cls.http=server.ThreadingHTTPServer(('127.0.0.1',0),QuietHandler);cls.base=f'http://127.0.0.1:{cls.http.server_port}'
        cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):cls.http.shutdown();cls.http.server_close();cls.temp.cleanup()
    def post(self,name,content,origin=None):
        data=json.dumps({'name':name,'content':content}).encode();req=urllib.request.Request(self.base+'/api/export',data=data,headers={'Origin':origin or self.base,'Content-Type':'application/json'})
        return urllib.request.urlopen(req)
    def test_same_origin_unicode_export(self):
        with self.post('StreamSignal_test.csv','\ufeffcity,note\nCoimbra,"access & <sample>"') as response:out=json.load(response)
        with urllib.request.urlopen(self.base+'/'+out['url']) as response:self.assertEqual(response.read().decode(),'\ufeffcity,note\nCoimbra,"access & <sample>"')
    def test_no_overwrite(self):
        urls=[]
        for value in ['first','second']:
            with self.post('StreamSignal_duplicate.json',value) as response:urls.append(json.load(response)['url'])
        self.assertNotEqual(*urls)
        self.assertEqual((server.ROOT/urls[0]).read_text(),'first')
    def test_foreign_origin_rejected(self):
        with self.assertRaises(urllib.error.HTTPError) as error:self.post('StreamSignal_bad.csv','x','https://example.com')
        self.assertEqual(error.exception.code,403)
    def test_path_escape_rejected(self):
        with self.assertRaises(urllib.error.HTTPError) as error:self.post('../outside.csv','x')
        self.assertEqual(error.exception.code,400)
    def test_invalid_type_rejected(self):
        with self.assertRaises(urllib.error.HTTPError) as error:self.post('StreamSignal_invalid.json',{'not':'text'})
        self.assertEqual(error.exception.code,400)
