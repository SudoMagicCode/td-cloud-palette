import requests
import json
import listerDataInterface


api_host = "https://znkbfhltad.execute-api.us-east-1.amazonaws.com"

class SaveOp:
    def __init__(self, tdOperator: callable, opCache: callable, accessToken: str) -> None:
        self._cache = opCache

        self._source_op = tdOperator
        self._source_id = tdOperator.id

        self._copy_to_upload = None
        self._copy_to_upload_id = None

        self.author: str = ''
        self.tox_name: str = ''
        self.assetType: listerDataInterface.cloudPaletteType = listerDataInterface.cloudPaletteType.notYetAssigned
        self.folder: str = ''
        self.TD_version = ''
        self.TD_build = ''
        self.Tox_version = ''
        self.accessToken = accessToken

        self.copy_to_buffer()

    @property
    def External_op(self):
        return self._copy_to_upload

    def _convert_par_to_asset_type(self, assetType: str) -> listerDataInterface.cloudPaletteType:
        par_map = {
            'tdComp': listerDataInterface.cloudPaletteType.tdComp,
            'tdTemplate': listerDataInterface.cloudPaletteType.tdTemplate
        }
        return par_map.get(assetType, listerDataInterface.cloudPaletteType.notYetAssigned)

    def generate_pars(self) -> None:
        # first update all attributes for our save op
        self.author = ipar.UploadSettings.Author.eval()
        self.tox_name = ipar.UploadSettings.Toxname.eval()
        self.assetType = self._convert_par_to_asset_type(
            ipar.UploadSettings.Assettype.eval())
        self.folder = ipar.UploadSettings.Userdirs.eval()
        self.TD_version = app.version
        self.TD_build = app.build
        self.Tox_version = ipar.UploadSettings.Toxversionpreview.eval()

        # generate all custom pars
        self.custom_page_setup(self._copy_to_upload)

    def update_custom_str_par(self, targetOp: callable, par: callable, value: str, par_label: str = "Temp"):
        if targetOp.par[par] != None:
            targetOp.par[par] = value
        else:
            about_page = targetOp.appendCustomPage("About")
            about_page.appendStr(par, label=par_label)
            targetOp.par[par] = value
            targetOp.par[par].readOnly = True

    def custom_page_setup(self, target_op: callable):
        self.update_custom_str_par(
            target_op,
            "Author",
            self.author,
            "Author")

        self.update_custom_str_par(
            target_op,
            "Toxname",
            self.tox_name,
            "Tox Name")

        self.update_custom_str_par(
            target_op,
            "Assettype",
            self.assetType.value,
            "Asset Type")

        self.update_custom_str_par(
            target_op,
            "Toxversion",
            "1.0.0",
            "Tox Version")

        self.update_custom_str_par(
            target_op,
            "Tdversion",
            app.version,
            "TD Version")

        self.update_custom_str_par(
            target_op,
            "Tdbuild",
            app.build,
            "TD Build")

        self.update_custom_str_par(
            target_op,
            "Lastsaved",
            datetime.datetime.now(),
            "Last Saved")

    def _clean_up_buffer(self) -> None:
        '''Ensures there is only one op in the buffer
        '''
        buffer_ops = self._cache.findChildren(depth=1)
        for each_op in buffer_ops:
            each_op.destroy()

    def copy_to_buffer(self) -> None:
        '''Copies source op to buffer
        '''
        self._clean_up_buffer()
        self._copy_to_upload = self._cache.copy(self._source_op)
        self._copy_to_upload_id = self._copy_to_upload.id
        self._copy_to_upload.nodeX = 0
        self._copy_to_upload.nodeY = 0

    def remove_external_file_refs(self) -> None:
        external_text_ops = self._copy_to_upload.findChildren()

        for each_child in external_text_ops:
            ...

    def upload_to_cloud(self) -> None:
        copyData = self._copy_to_upload.saveByteArray()

        meta_data = {
            "name": self.tox_name,
            "path": self.folder,
            "access_token": self.accessToken
        }

        d = json.dumps(meta_data)
        req = requests.put(api_host+'/palette', d, headers={"content-type":"application/json"})
        print(req.text)
        result = req.json()
        object_put = requests.put(result['url'], copyData)
        if(object_put.status_code == 200):
            print("successfully uploaded")


    def save(self) -> None:
        # add pars to op
        self.generate_pars()

        # fix up comp name
        self._copy_to_upload.name = f'{self._copy_to_upload.type}_{tdu.validName(self.tox_name)}'

        # remove all external text files
        self.remove_external_file_refs()

        # whatever else needs to happen
        self.upload_to_cloud()
