""" downloaded from http://xbmc-addons.googlecode.com/svn/addons/ """
""" This is a modded version of the original addons.xml generator """

""" Put this version in the root folder of your repo and it will """
""" zip up all add-on folders, create a new zip in your zips folder """
""" and then update the md5 and addons.xml file """


import os
import shutil
import hashlib
import zipfile
import xml.etree.ElementTree as ET

class Generator:
    """
        Generates a new addons.xml file from each addons addon.xml file
        and a new addons.xml.md5 hash file. Must be run from the root of
        the checked-out repo. Only handles single depth folder structure.
    """
    def __init__(self):
# Create the zips folder if it doesn't already exist
        self.zips_path = 'zips'
        if not os.path.exists(self.zips_path):
            os.makedirs(self.zips_path)

        self.addons_file = os.path.join(self.zips_path, 'addons.xml')

# Comment out this line if you have .pyc or .pyo files you need to keep
        self._remove_binaries()

        self._generate_addons_file()
        self._generate_md5_file()
        print("Finished updating addons xml and md5 files")

    def Create_Zips(self, addon_id, version, copyfiles):
        addon_folder = os.path.join(self.zips_path, addon_id)
        if not os.path.exists(addon_folder):
            os.makedirs(addon_folder)

        final_zip = os.path.join(self.zips_path, addon_id, f'{addon_id}-{version}.zip')
        if not os.path.exists(final_zip):
            print(f'NEW ADD-ON - Creating zip for: {addon_id} v.{version}')
            zip = zipfile.ZipFile(final_zip, 'w', compression=zipfile.ZIP_DEFLATED)
            root_len = len(os.path.dirname(os.path.abspath(addon_id)))
            for root, dirs, files in os.walk(addon_id):
                archive_root = os.path.abspath(root)[root_len:]
                for f in files:
                        fullpath = os.path.join(root, f)
                        archive_name = os.path.join(archive_root, f)
                        zip.write(fullpath, archive_name, zipfile.ZIP_DEFLATED)
            zip.close()
            
# Copy over the icon, fanart and addon.xml to the zip directory
            for file in copyfiles:
                if file and os.path.exists(file):
                    shutil.copy(file, addon_folder)
                    pass

# Remove any instances of pyc or pyo files
    def _remove_binaries(self):
        for parent, dirnames, filenames in os.walk('.'):
            for fn in filenames:
                if fn.lower().endswith('pyo') or fn.lower().endswith('pyc'):
                    compiled = os.path.join(parent, fn)
                    py_file = compiled.replace('.pyo', '.py').replace('.pyc', '.py')
                    if os.path.exists(py_file):
                        try:
                            os.remove(compiled)
                            print('Removed compiled python file:')
                            print(compiled)
                            print('-----------------------------')
                        except:
                            print('Failed to remove compiled python file:')
                            print(compiled)
                            print('-----------------------------')
                    else:
                        print('Compiled python file found but no matching .py file exists:')
                        print(compiled)
                        print('-----------------------------')

    def _generate_addons_file(self):
# addon list
        addons = os.listdir('.')
        addons_root = ET.Element('addons')
# loop thru and add each addons addon.xml file
        for addon in addons:
            try:
                if (not os.path.isdir(addon) or addon == self.zips_path or addon.startswith('.')): continue
                _path = os.path.join(addon, "addon.xml")
                _tree = ET.parse(_path)
                _root = _tree.getroot()
                version = _root.attrib['version']
                #scan 'assets' tag for locations
                try:
                    _icon = _root.find(f'.//icon').text.split('/')
                    _icon = os.path.join(addon, *_icon)
                except: _icon = None
                try:
                    _fanart = _root.find(f'.//fanart').text.split('/')
                    _fanart = os.path.join(addon, *_fanart)
                except: _fanart = None

                files = [_icon, _fanart]
                addons_root.append(_root)

# Create the zip files                
                self.Create_Zips(addon, version, files)

            except Exception as e:
                print(f'Excluding {_path} for {repr(e)}')
# clean and save addons.xml

        addons_xml = ET.ElementTree(self.indent(addons_root))
        try:
            addons_xml.write(self.addons_file, xml_declaration=True, encoding='utf-8')
        except Exception as e:
            print(f"An error occurred saving {self.addons_file} file!\n{repr(e)}")

    def _generate_md5_file(self):
        try:
            m = hashlib.md5(open(self.addons_file).read().encode('utf8')).hexdigest()
            open(os.path.join(self.zips_path, 'addons.xml.md5'), 'w').write(m)

        except Exception as e:
            print(f"An error occurred creating addons.xml.md5 file!\n{repr(e)}")

    # pretty print method

    def indent(self, elem, level=0):
        i = "\n" + level * "  "
        j = "\n" + (level - 1) * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for subelem in elem:
                self.indent(subelem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = j
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = j
        return elem


if ( __name__ == "__main__" ):
    Generator()