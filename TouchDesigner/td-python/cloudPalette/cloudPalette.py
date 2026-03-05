import json
import os
import shutil
import listerDataInterface
import remoteSources
import tdi
import pathlib
import downloader
import decoratedLog
import cloudPaletteType

CLOUD_PALETTE: str = 'cloudPalette.json'
CLOUD_PALETTE_LOCK: str = 'cloudPalette.lock'
LAST_CACHE: str = 'userInventory.json'


class PaletteExplorer:
    '''
    '''

    def __init__(self, myOp: tdi.baseCOMP):
        '''
        '''

        self.__repr__ = 'Class <PaletteExplorer>'
        self.MyOp = myOp
        self.opShell: baseCOMP = myOp.parent()

        self.log_decorator = "CLOUD PALETTE"
        self.decoratedLog = decoratedLog.DecoratedLog(
            logDecorator=self.log_decorator)

        self.inventory_blocks = []
        self.Has_inventory = False
        self.current_tox_info: dict = {}
        self._local_tox_cache: pathlib.Path = None

        # Data structures for remote data
        self.remote_collections: list[remoteSources.RemoteCollection] = []

        self.Remote_assets: dict = {}
        self.Remote_data: list[cloudPaletteType.cloudPaletteCollection] = []
        self._inventory_data: dict = {}
        self.Remote_sources: list[remoteSources.RemoteSource] = []
        self.remote_sources_map: dict = {}

        self._asset_tree_list = tdu.Dependency([])

        self._local_cache: baseCOMP = myOp.op(
            'base_cloud_palette_cache/base_empty')
        self.PaletteWindowCOMP: windowCOMP = myOp.op('window_palette')
        self.PlacementWindowCOMP: windowCOMP = myOp.op('window_placement')
        self.CloudPalette_pop_menu_COMP = myOp.op('popMenu')
        self.Popup_tox_info_COMP = myOp.op('widget_popup_tox_info')
        self.Popup_tox_dl_COMP = myOp.op('widget_dl_info')
        self._td_palette_DAT = myOp.op('null_td_palette')
        self.webClientDAT: webclientDAT = myOp.op('webclient_palette')
        self.asset_treeDAT: scriptDAT = myOp.op('script_asset_tree')
        self._lister_COMP = myOp.op(
            "container_treeLister_palette/container_body/container_palette/treeLister")
        self._search_text_COMP = myOp.op(
            "container_tree_lister/container_body/container_palette/container_search/text_search")

        self._setup()

        self.decoratedLog.log_to_textport(f'PaletteExplorer init from {myOp}')

    @property
    def Asset_tree_list(self) -> list:
        return self._asset_tree_list

    @property
    def Local_tox_cache(self) -> str:
        return self._local_tox_cache

    def Get_treeLister_data(self) -> dict:
        data_dict = {}
        return data_dict

    def get_local_tox_path(self, localPath: str) -> str:
        return f'{self.Local_tox_cache}/{localPath}'

    @property
    def user_cache_file(self) -> str:
        return f'{self.Local_tox_cache}/{LAST_CACHE}'

    @property
    def palette_file(self) -> str:
        return f'{self.Local_tox_cache}/{CLOUD_PALETTE}'

    @property
    def palette_lock_file(self) -> str:
        return f'{self.Local_tox_cache}/{CLOUD_PALETTE_LOCK}'

    def _setup(self) -> None:
        """All set-up procedures for UI"""
        self.opShell.par.Localcache = ''

        # resets lister
        self._lister_COMP.par.Refresh.pulse()

        # check for and build a local cache
        self._check_local_tox_cache()

        self._check_cache_file()

    def _query_cloud(self,) -> None:
        '''
        '''
        pass

    def _check_cache_file(self) -> None:
        if os.path.exists(self.user_cache_file):
            self._load_user_cache_file()

    def _load_user_cache_file(self) -> None:

        with open(self.user_cache_file, 'r') as json_file:
            self._inventory_data = json.load(json_file)

        self._gather_remote_sources()

        # refresh assets
        self._query_cloud()

    def Load_inventory(self) -> None:
        self.decoratedLog.log_to_textport('Importing cloud palette inventory')

        # user selects file
        inventory_file = ui.chooseFile(
            title="Select an Inventory", fileTypes=['json'])

        # overwrite existing cache file with user selection
        with open(self.user_cache_file, 'w') as destination, open(inventory_file, 'r') as source:
            content = source.read()
            destination.write(content)

        # load newly overwritten file
        self._load_user_cache_file()

    def Delete_local_cache(self) -> None:
        self.decoratedLog.log_to_textport('Deleting local cache files')
        self.delete_cache()

    def delete_cache(self) -> None:
        cache_path = pathlib.Path(self.Local_tox_cache)
        subdirs = [each for each in cache_path.iterdir() if each.is_dir()]

        for each_subdir in subdirs:
            shutil.rmtree(each_subdir)

    def Download_tox_files(self) -> None:
        # cleanup old files
        self.delete_cache()

        # show popup to warn the user that we're downloading
        self.Popup_tox_dl_COMP.par.Openui.pulse()

        # run our download process
        run(self._download_remote_tox_files, delayFrames=5)

    def _download_remote_tox_files(self) -> None:
        files_list: list[downloader.dl_target] = []

        for each in self.remote_collections:
            for each_source in each.sources:
                if each_source.paletteCollection == None:
                    pass
                else:
                    for each_asset in each_source.paletteCollection.collection:
                        if each_asset.assetType != cloudPaletteType.paletteType.folder:
                            new_dl_target = downloader.dl_target(
                                name=each_asset.display_name,
                                author=each_asset.author,
                                path=f'{self.Local_tox_cache}/{each_asset.asset_local_path}',
                                url=each_asset.asset_url)

                            files_list.append(new_dl_target)

        downloader.download(
            worker_info=files_list, targetOP=self.MyOp)

        self.Popup_tox_dl_COMP.par.Closeui.pulse()

    def _dump_remote_data(self) -> None:
        with open(f'{self.Local_tox_cache}/cloudPaletteData.json', 'w') as cloudPaletteFile:
            data = json.dumps(self.Remote_data, indent=4)
            cloudPaletteFile.write(data)

    def _check_local_tox_cache(self) -> None:
        derivative_folder = pathlib.Path(app.userPaletteFolder).parent
        cloud_palette_folder = pathlib.Path(
            f"{derivative_folder}/cloudPalette")
        if os.path.isdir(cloud_palette_folder):
            pass
        else:
            self.decoratedLog.log_to_textport(
                f'creating directory {cloud_palette_folder}')
            os.makedirs(cloud_palette_folder)

        self._local_tox_cache = cloud_palette_folder
        self.opShell.par.Localcache = cloud_palette_folder

    def _gather_remote_sources(self):
        # empty remote sources
        self.remote_collections.clear()
        self.Remote_sources.clear()
        self.remote_sources_map.clear()

        sources = self._inventory_data.get('paletteElements')

        print('gathering remotes')

        # rebuild remote sources based on contents
        for each_collection in sources:
            new_invio_collection = remoteSources.InvioCollection.fromJson(
                json=each_collection)
            new_remote_collection = remoteSources.RemoteCollection.fromInvioCollection(
                new_invio_collection)

            self.remote_collections.append(new_remote_collection)

            for each_source in new_invio_collection.sources:
                new_remote = remoteSources.RemoteSource.fromInvioSource(
                    new_remote_collection.name, each_source)

                # self.Remote_sources.append(new_remote)
                self.remote_sources_map[new_remote.remote] = new_remote.name

                # get remote data
                self.decoratedLog.log_to_textport(
                    f"remote source {new_remote.name}")
                self.webClientDAT.request(
                    new_remote.remote_inventory, "GET")

    def Refresh_inventory(self):
        self._set_ui_status('Refreshing Inventory')
        self._query_cloud()

    def Parse_cloud_response(self, data, headerDict: dict):
        '''
        '''
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
                        self.handle_inventory_return(data=data)

                    case "tox":
                        self.CreatePaletteTOX(
                            request_response=data, from_bytes=True)
                        self.current_tox_info = {}

                    case _:
                        pass
            case _:
                pass

    def handle_inventory_return(self, data: dict) -> None:

        # loop through our collections and ensure the data finds its way home
        for each_remote_collection in self.remote_collections:
            for each_remote_source in each_remote_collection.sources:
                each_remote_source.collection_name = each_remote_collection.name

                new_cloud_palette_collection = cloudPaletteType.cloudPaletteCollection.from_json(
                    data, remoteSources=self.remote_sources_map, root=each_remote_source.collection_name)

                if new_cloud_palette_collection.source == each_remote_source.remote:
                    each_remote_source.paletteCollection = new_cloud_palette_collection
                    break

        self.asset_treeDAT.cook(force=True)

    def PaletteWindow(self, state) -> None:
        '''
        '''

        if state:
            # start with a fresh search filter
            self._clear_search()

            # open window COMP
            self.PaletteWindowCOMP.par.winopen.pulse()
        else:
            self.PaletteWindowCOMP.par.winclose.pulse()

        pass

    def PlacementWindow(self, state) -> None:
        '''
        '''
        if state:
            self.PlacementWindowCOMP.par.winopen.pulse()
        else:
            self.PlacementWindowCOMP.par.winclose.pulse()

        pass

    def FindToxToLoad(self, info: dict) -> dict:
        '''
        '''
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

            local_path: str = self.get_local_tox_path(localPath=info.get(
                'rowData').get('rowObject').get('local_asset_path'))
            remote_path: str = info.get(
                'rowData').get('rowObject').get('asset_url')

            isLocal: bool = os.path.isfile(local_path)

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
        '''
        '''
        currentPane = ui.panes[ui.panes.current]
        networkPath = currentPane.owner
        return networkPath

    def GetCurrentPane(self) -> callable:
        '''
        '''
        return ui.panes[ui.panes.current]

    def RequestRemoteToxAsset(self, tox_info: dict) -> None:
        '''
        '''
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
        '''
        '''
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
        '''
        '''

        OpBuffer = self._local_cache
        old_ops = OpBuffer.findChildren()

        for each_child in old_ops:
            each_child.destroy()

        return OpBuffer

    def OpBufferDestroy(self, OpBuffer) -> None:
        '''
        '''
        OpBuffer.destroy()
        pass

    def PlacePaletteTox(self, info: dict) -> None:
        '''
        '''
        row: int = info.get('row')

        if row == -1:
            pass
        else:
            tox_info = self.FindToxToLoad(info)

            if tox_info.get('safe_to_load'):
                match tox_info.get('is_local'):
                    case True:
                        self.current_tox_info = tox_info
                        self.GetLocalToxAsset(tox_info)
                    case _:
                        self.RequestRemoteToxAsset(tox_info)
            else:
                pass
            pass

    def Open_palette(self) -> None:
        '''
        '''
        parent.tool.PaletteWindow(True)

    def check_privacy(self) -> bool:
        '''
        '''
        # check to see comp privacy is active
        is_private = self.MyOp.par.Compsource.eval().isPrivate
        privacy_active = self.MyOp.par.Compsource.eval().isPrivacyActive

        if is_private and not privacy_active:
            return True
        else:
            return False

    def get_item_from_row_index(self, index: int) -> dict:
        '''
        '''
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

                        menuItems: list = [
                            'Show TOX Info']

                        self.CloudPalette_pop_menu_COMP.Open(
                            items=menuItems,
                            callback=onMenuChoice,
                            callbackDetails={'lister_row_data': info}
                        )

                        pass

    def Edit_search(self, search_val: str) -> None:
        """Updates filter string par
        """
        self._lister_COMP.par.Filterstring = search_val

    def _clear_search(self) -> None:
        """Clears filter string"""
        self.MyOp.op('iparUiKit').par.Searchstring = ''

    def _set_ui_status(self, msg: str) -> None:
        '''
        '''
        ui.status = f'{self.log_decorator} | {msg}'

    @property
    def Build_lister_asset_tree(self) -> list:
        '''
        '''
        # clear asset tree list
        self._asset_tree_list = tdu.Dependency([])
        self._asset_tree_list.val.append(
            [each for each in listerDataInterface.header_map.keys()])

        # add all elements from remotes
        self._add_asset_tree_elements_from_remotes()

        return self._asset_tree_list

    def _add_asset_tree_elements_from_remotes(self) -> None:
        '''
        '''

        for each in self.remote_collections:
            new_author_row = listerDataInterface.AuthorRow(root=each.name)
            self._asset_tree_list.val.append(new_author_row.as_list)

            for each_source in each.sources:
                if each_source.paletteCollection == None:
                    pass
                else:
                    new_folder_row = listerDataInterface.FolderRow(
                        root=each.name)
                    new_folder_row.cloudAsset = each_source
                    new_folder_row.cloudAsset.sub_dir = each_source.paletteCollection.sub_dir
                    self._asset_tree_list.val.append(
                        new_folder_row.as_list)

                    for each_asset in each_source.paletteCollection.collection:
                        new_lister_row = listerDataInterface.AssetRow(
                            root=each.name, cloudAsset=each_asset)
                        self._asset_tree_list.val.append(
                            new_lister_row.as_list)

    def _add_asset_tree_elements_from_table(self, author: str, tableSource: OP) -> None:
        '''
        '''

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
