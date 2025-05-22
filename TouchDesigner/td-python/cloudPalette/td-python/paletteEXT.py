import json
import os
import listerDataInterface
import remoteSources
import saveUtils


class PaletteExplorer:
    """
    """

    def __init__(self, myOp: op):
        """
        """
        self.__repr__ = 'Class <PaletteExplorer>'
        self.inventory: str = 'https://sudo-tools-td-templates.sudo.codes/builds/latest/inventory.json'
        self.inventory_blocks = []
        self.Has_inventory = False
        self.log_decorator = "CLOUD PALETTE"
        self.access_token_file: str = f'{app.preferencesFolder}/cloudPaletteAccessToken.txt'
        self.access_token: str = ""
        self.Has_access_token = tdu.Dependency(False)
        self.Check_access_token()
        self.Remote_sources: list[remoteSources.RemoteSources] = []

        self.MyOp = myOp

        self._local_cache = myOp.op('base_cloud_palette_cache/base_empty')
        self._preflight_cache = myOp.op(
            'base_cloud_palette_cache/base_preflight')
        self.upload_settings_COMP = myOp.op('iparUploadSettings')

        self.Remote_assets: dict = {}

        self.Remote_data: dict = []

        self.PaletteWindowCOMP = myOp.op('window_palette')
        self.PlacementWindowCOMP = myOp.op('window_placement')
        self.CloudPalette_pop_menu_COMP = myOp.op('popMenu')
        self.Popup_tox_info_COMP = myOp.op('widget_popup_tox_info')

        self._td_palette_DAT = myOp.op('null_td_palette')

        self.webClientDAT = myOp.op('webclient_palette')
        self.asset_treeDAT = myOp.op('script_asset_tree')

        self._lister_COMP = myOp.op(
            "container_treeLister_palette/container_body/container_palette/treeLister")

        self._search_text_COMP = myOp.op(
            "container_tree_lister/container_body/container_palette/container_search/text_search")

        self.current_tox_info: dict = {}

        self._upload_op: callable = None

        self._asset_tree_list = tdu.Dependency([])

        self._setup()

        print(f'PaletteExplorer init from {myOp}')

        pass

    @property
    def Asset_tree_list(self) -> list:
        return self._asset_tree_list

    def Get_treeLister_data(self) -> dict:
        data_dict = {}
        return data_dict

    def Check_access_token(self):
        if os.path.isfile(self.access_token_file):
            # validate api key
            self.Has_access_token.val = True
            with open(self.access_token_file, "r") as f:
                self.access_token = f.read()
        else:
            self.Has_access_token.val = False

    def add_access_token(self, access_token: str) -> str:
        with open(self.access_token_file, 'w+') as file:
            print('[~] CloudPalette - adding access token')
            file.write(access_token)

    def remove_access_token(self) -> None:
        print('[~] CloudPalette - removing access token')
        if self.Has_access_token.val:
            # delete access token
            os.remove(self.access_token_file)
            # update status of access token
            self.Has_access_token.val = False

    def Add_api_key(self) -> None:
        def dialogChoice(info):
            button_choice = info.get('buttonNum')
            access_token = info.get('enteredText')
            print(info)
            match button_choice:
                case 2:
                    if access_token == '':
                        print('[~] missing api key')
                    else:
                        self.add_access_token(access_token)
                        self.Check_access_token()
                case _:
                    pass

        op.TDResources.PopDialog.OpenDefault(
            title='CloudPalette Config',
            text='Add a CloudPalette API Key',
            textEntry=True,
            buttons=['Cancel', 'Add'],
            escButton=1,
            enterButton=1,
            callback=dialogChoice
        )

    def _setup(self) -> None:
        """All set-up procedures for UI"""
        # resets lister
        self._lister_COMP.par.Refresh.pulse()

        self._gather_remote_sources()

        # refresh assets
        self._query_cloud()

    def _query_cloud(self,) -> None:
        """
        """
        # set url for inventory
        self.webClientDAT.par.url = self.inventory
        # pulse par and wait for response
        self.webClientDAT.par.request.pulse()

    def _gather_remote_sources(self):
        # empty remote sources
        self.Remote_sources.clear()

        # rebuild remote sources based on contents
        for each_block in parent.cloudPalette.seq.Remotesources.blocks:
            new_remote = remoteSources.RemoteSources.sourceFromBlock(
                each_block)
            self.Remote_sources.append(new_remote)

            # get remote data
            print(f"remote source {new_remote.name}")
            self.webClientDAT.par.url = new_remote.remote
            self.webClientDAT.par.request.pulse()

    def Refresh_inventory(self):
        self._set_ui_status('Refreshing Inventory')
        self._query_cloud()

    def Parse_cloud_response(self, data, headerDict: dict):
        """
        """

        match headerDict.get('content-type'):
            case 'binary/octet-stream':
                # we've downloaded a tox
                self.CreatePaletteTOX(request_response=data, from_bytes=True)
                self.current_tox_info = {}

            case 'application/json':
                # we got back our inventory
                self.Remote_assets = json.loads(data.decode())
                self.Has_inventory = True
                self.asset_treeDAT.cook(force=True)

            case 'application/octet-stream':
                disposition: str = headerDict.get(
                    "content-disposition", ".").split(".")[-1]

                match disposition:
                    case "json":
                        # NOTE KEEP TRACK HERE
                        data: dict = json.loads(data.decode())
                        self.Remote_data.append(data)
                        self.asset_treeDAT.cook(force=True)
                    case _:
                        pass
            case _:
                pass

    def PaletteWindow(self, state) -> None:
        """
        """

        if state:
            # start with a fresh search filter
            self._clear_search()

            # open window COMP
            self.PaletteWindowCOMP.par.winopen.pulse()
        else:
            self.PaletteWindowCOMP.par.winclose.pulse()

        pass

    def PlacementWindow(self, state) -> None:
        """
        """
        if state:
            self.PlacementWindowCOMP.par.winopen.pulse()
        else:
            self.PlacementWindowCOMP.par.winclose.pulse()

        pass

    def FindToxToLoad(self, info: dict) -> dict:
        """
        """
        row = info.get('row')
        col = info.get('col')
        TOXPath = None

        is_tox: bool = True if info.get('rowData').get(
            'rowObject').get('isTOX') == 'True' else False

        load_info = {
            'safe_to_load': None,
            'is_local': False,
            'remote_path': None,
            'local_path': None,
            'selected_tox_name': None,
            'type': None,
        }

        if is_tox:
            isLocal: bool = True if info.get('rowData').get(
                'rowObject').get('isLocal') == 'True' else False
            local_path: str = info.get(
                'rowData').get('rowObject').get('local_asset_path')
            remote_path: str = info.get(
                'rowData').get('rowObject').get('asset_url')

            load_info['safe_to_load'] = is_tox
            load_info['is_local'] = isLocal
            load_info['local_path'] = local_path
            load_info['remote_path'] = remote_path
            load_info['selected_tox_name'] = info.get(
                'rowData').get('rowObject').get('name')
            load_info['type'] = info.get(
                'rowData').get('rowObject').get('assetType')

            self.PaletteWindow(False)

            return load_info

        else:
            load_info['safe_to_load'] = is_tox
            return load_info

    def GetCurrentNetworkLocation(self) -> callable:
        """
        """
        currentPane = ui.panes[ui.panes.current]
        networkPath = currentPane.owner
        return networkPath

    def GetCurrentPane(self) -> callable:
        """
        """
        return ui.panes[ui.panes.current]

    def RequestRemoteToxAsset(self, tox_info: dict) -> None:
        """
        """
        # request TOX with web client DAT
        self.webClientDAT.par.url = tox_info.get('remote_path')
        self.webClientDAT.par.request.pulse()

        # update the temp variable for tox info
        self.current_tox_info = tox_info

    def GetLocalToxAsset(self, tox_info: dict) -> None:
        self.CreatePaletteTOX(
            from_bytes=False, file_path=tox_info.get('local_path'))

    def CreatePaletteTOX(
            self,
            from_bytes: bool = False,
            file_path: str = '',
            request_response: bytes = None) -> None:
        """
        """
        tox_info = self.current_tox_info

        OpBuffer = self.OpBufferCreate()
        networkPath = self.GetCurrentNetworkLocation()

        if from_bytes:
            paletteTOX = OpBuffer.loadByteArray(request_response)
        else:
            paletteTOX = OpBuffer.loadTox(file_path)

        self.current_tox_info = tox_info

        # place template
        template = OpBuffer.copy(paletteTOX)
        template.nodeX = 200
        template.nodeY = 0

        # destroy containing op
        paletteTOX.destroy()

        if tox_info.get('type') == 'tdTemplate':
            op_list = template.findChildren(depth=1)
            ui.copyOPs(op_list)
            self.GetCurrentPane().placeOPs(op_list)

        else:
            # clear pars on template
            template.par.clone = ''
            template.par.externaltox = ''
            # Use TD's built in op placement toolkit
            ui.copyOPs([template])
            self.GetCurrentPane().placeOPs([template])

        pass

    def OpBufferCreate(self) -> callable:
        """
        """

        OpBuffer = self._local_cache

        old_ops = OpBuffer.findChildren()

        for each_child in old_ops:
            each_child.destroy()

        return OpBuffer

    def OpBufferDestroy(self, OpBuffer) -> None:
        """
        """
        OpBuffer.destroy()
        pass

    def PlacePaletteTox(self, info: dict) -> None:
        """
        """
        row: int = info.get('row')
        if row == -1:
            pass
        else:
            tox_info = self.FindToxToLoad(info)

            if tox_info.get('safe_to_load'):
                match tox_info.get('is_local'):
                    case True:
                        self.GetLocalToxAsset(tox_info)
                    case _:
                        self.RequestRemoteToxAsset(tox_info)
            else:
                pass
            pass

    def Open_palette(self) -> None:
        """
        """
        parent.tool.PaletteWindow(True)
        # privacy = self.check_privacy()
        # if privacy:
        # parent.tool.PaletteWindow(True)
        # else:
        # self.prompt_password()

    def check_privacy(self) -> bool:
        """
        """
        # check to see comp privacy is active
        is_private = self.MyOp.par.Compsource.eval().isPrivate
        privacy_active = self.MyOp.par.Compsource.eval().isPrivacyActive

        if is_private and not privacy_active:
            return True
        else:
            return False

    def get_item_from_row_index(self, index: int) -> dict:
        info = {}

        info['asset_tree_row':self.asset_treeDAT.row(index)]

        return info

    def On_lister_right_click(self, info: dict) -> None:
        '''Handles lister right click events'''
        row: int = info.get('row')

        match row:
            case -1:
                # we've clicked on the bottom of the lister
                pass
            case _:
                assetType: str = info.get('rowData').get('rowObject').get(
                    'assetType', 'unknown')

                match assetType:
                    case 'folder':
                        pass

                    case 'unknown':
                        pass
                    case _:
                        def onMenuChoice(info):
                            menuChoice: int = info.get('index')

                            toxName: str = info.get('details').get('lister_row_data').get('rowData').get(
                                'rowObject').get('name')

                            toxVersion: str = info.get('details').get('lister_row_data').get('rowData').get(
                                'rowObject').get('TOXVersion')

                            tdVersion: str = info.get('details').get('lister_row_data').get('rowData').get(
                                'rowObject').get('TDVersion')

                            lastSaved: str = info.get('details').get('lister_row_data').get('rowData').get(
                                'rowObject').get('lastSaved')

                            match menuChoice:
                                case 0:
                                    self.Popup_tox_info_COMP.par.Title = f'{toxName} Details'
                                    self.Popup_tox_info_COMP.par.Toxversion = toxVersion
                                    self.Popup_tox_info_COMP.par.Tdversion = tdVersion
                                    self.Popup_tox_info_COMP.par.Lastsaved = lastSaved
                                    self.Popup_tox_info_COMP.par.Openui.pulse()
                                case 1:
                                    # the user wants to update an existing TOX
                                    ...
                                case _:
                                    pass

                            print(toxVersion)

                        menuItems: list = [
                            'Show TOX Info', 'Upload Update']

                        self.CloudPalette_pop_menu_COMP.Open(
                            items=menuItems,
                            callback=onMenuChoice,
                            callbackDetails={'lister_row_data': info}
                        )

                        pass

    def Palette_drop_event(self, comp: op, info: dict) -> None:
        '''handles palette drop event'''
        to_be_uploaded_op = info.get('dragItems')
        self._upload_op = saveUtils.SaveOp(
            tdOperator=to_be_uploaded_op[0], opCache=self._preflight_cache, accessToken=self.access_token)
        self.upload_settings_COMP.par.Showuploadsettings = True

    def Upload_tox_to_cloud(self) -> None:
        '''uploads tox to the cloud'''
        self._upload_op.save()
        self.upload_settings_COMP.par.Showuploadsettings = False
        parent.cloudPalette.par.Showuploadzone = False
        self._clear_upload_settings()

    def Cancel_upload(self) -> None:
        self.upload_settings_COMP.par.Showuploadsettings = False
        self._clear_upload_settings()

    def _clear_upload_settings(self) -> None:
        pars = ['Author', 'Toxname', 'Toxversion1',
                'Toxversion2', 'Toxversion3']
        for each_par in pars:
            default_value = self.upload_settings_COMP.par[each_par].default
            self.upload_settings_COMP.par[each_par] = default_value

    def prompt_password(self) -> None:
        """
        """
        op('../base_license').par.Openlicensewindow.pulse()

    def Edit_search(self, search_val: str) -> None:
        """Updates filter string par
        """
        self._lister_COMP.par.Filterstring = search_val

    def _clear_search(self) -> None:
        """Clears filter string"""
        self.MyOp.op('iparUiKit').par.Searchstring = ''

    def _set_ui_status(self, msg: str) -> None:
        ui.status = f'{self.log_decorator} | {msg}'

    @property
    def Build_lister_asset_tree(self) -> list:
        # clear asset tree list
        self._asset_tree_list = tdu.Dependency([])
        self._asset_tree_list.val.append(listerDataInterface.header_row)

        # add all elements from API
        # self._add_asset_tree_elements_from_api()

        # add all elements from remotes
        self._add_asset_tree_elements_from_remotes()

        # add all elements from folder DAT
        # self._add_asset_tree_elements_from_table(
        #     author='Derivative', tableSource=self._td_palette_DAT)

        return self._asset_tree_list

    def _add_asset_tree_elements_from_remotes(self) -> None:
        for each in self.Remote_data:
            collections = each.get("collections")
            for each_collection in collections:
                author: str = each_collection.get("author")
                author_row: listerDataInterface.TreeListerRow = listerDataInterface.TreeListerRow.from_github_response_folder_row(
                    author)
                self._asset_tree_list.val.append(author_row.as_list)

                for each_element in each_collection.get("contents", []):
                    new_row: listerDataInterface.TreeListerRow = listerDataInterface.TreeListerRow.from_github_response(
                        each_element, author)
                    try:
                        self._asset_tree_list.val.append(new_row.as_list)
                    except Exception as e:
                        print(e)

    def _add_asset_tree_elements_from_api(self) -> None:
        # reset user inventory blocks
        self.inventory_blocks = []

        new_row_data = {
            'author': '',
            'block': '',
            'base_uri': '',
            'asset_data': {}
        }

        try:
            new_row_data['base_uri'] = self.Remote_assets.get(
                'setup').get('base_uri')

            for each_author in self.Remote_assets.get('collections'):
                new_row_data['author'] = each_author.get('author')

                # build row for author - this is a folder
                new_row = listerDataInterface.TreeListerRow.folder_row(
                    data=new_row_data)
                self._asset_tree_list.val.append(new_row.as_list)
                # print('adding author row')

                for each_block in each_author.get('contents'):
                    new_row_data['block'] = each_block.get('block')

                    # build a row for the folder - this is a folder
                    new_row = listerDataInterface.TreeListerRow.folder_row(
                        data=new_row_data)

                    self._asset_tree_list.val.append(new_row.as_list)
                    # print('--->adding block row', each_block.get('block'))
                    self.inventory_blocks.append(each_block.get('block'))

                    for each_asset in each_block.get('assets'):
                        new_row_data['asset_data'] = each_asset

                        # build a row for the asset - his is an actual tox
                        new_row = listerDataInterface.TreeListerRow.from_api_response(
                            data=new_row_data)

                        self._asset_tree_list.val.append(new_row.as_list)
                        # print('------->adding asset row', new_row.display_name)

        except Exception as e:
            print('[~] Something went wrong adding rows from api data')
            print(e)

    def _add_asset_tree_elements_from_table(self, author: str, tableSource: op) -> None:
        headers = tableSource.row(0)

        header_lookup_map = {
            each_cell.val: each_cell.col for each_cell in headers}

        # add author row
        author_row = listerDataInterface.TreeListerRow.folder_row(
            data={'author': 'Derivative', 'block': ''})

        author_row.display_name = 'Derivative'
        self._asset_tree_list.val.append(author_row.as_list)

        for each_row in tableSource.rows()[1:]:
            new_row_data = {
                'author': author,
                'source_data': each_row
            }

            new_row = listerDataInterface.TreeListerRow.from_folder_dat(headerLookupMap=header_lookup_map,
                                                                        data=new_row_data)

            self._asset_tree_list.val.append(new_row.as_list)
