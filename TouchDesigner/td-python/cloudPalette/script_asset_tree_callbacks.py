# me - this DAT
# scriptOp - the OP which is cooking
#
# press 'Setup Parameters' in the OP to call this function to re-create the parameters.
def onSetupParameters(scriptOp):
    page = scriptOp.appendCustomPage('Custom')
    p = page.appendFloat('Valuea', label='Value A')
    p = page.appendFloat('Valueb', label='Value B')
    return

# called whenever custom pulse parameter is pushed


def onPulse(par):
    return


def onCook(scriptOp):
    scriptOp.clear()

    try:

        data: dict = parent.tool.Remote_assets
        base_uri: str = data.get('setup').get('base_uri')

        rows: list = []
        header: list = [
            'search_string',
            'name',
            'path',
            'isTOX',
            'asset_url',
            'type',
            'TDVersion',
            'TOXVersion',
            'lastSaved',
            'warn',
            'searchMatch',
            'hasCOMPs',
            'hasTOPs',
            'hasCHOPs',
            'hasSOPs',
            'hasMATs',
            'hasDATs']

        rows.append(header)

        lister_content: list = []

        for each_author in data.get('collections'):
            author: str = each_author.get('author')
            block_list: list = each_author.get('contents')

            author_row = [author, author,
                          f'creator/{author}', '', False, 'folder']
            rows.append(author_row)

            for each_block in block_list:
                block_name: str = each_block.get('block')
                block_path: str = f'creator/{author}/{block_name}'
                block_search: str = block_name
                assets: list = each_block.get('assets')
                block_row: list = [
                    block_search,
                    block_name,
                    block_path,
                    False,
                    '',
                    'folder']

                lister_content.append(block_row)

                for each_asset in assets:
                    asset_name: str = each_asset.get('display_name')
                    row_name: str = f'{asset_name}'
                    row_path: str = f'creator/{author}/{block_name}/{asset_name}'
                    row_search: str = f'{author} {block_name} {asset_name}'
                    row_url: str = f'''{
                        base_uri}latest/{each_asset.get('asset_path')}'''
                    tdVersion: str = each_asset.get('td_version')
                    toxVersion: str = each_asset.get('tox_version')
                    lastSaved: str = each_asset.get('last_updated')

                    warn: str = tdVersion != f'{app.version}.{app.build}'
                    hasCOMPs: bool = 'COMP' in each_asset.get('opFamilies'),
                    hasTOPs: bool = 'TOP' in each_asset.get('opFamilies'),
                    hasCHOPs: bool = 'CHOP' in each_asset.get('opFamilies'),
                    hasSOPs: bool = 'SOP' in each_asset.get('opFamilies'),
                    hasMATs: bool = 'MAT' in each_asset.get('opFamilies'),
                    hasDATs: bool = 'DAT' in each_asset.get('opFamilies'),
                    searchMatch: bool = matchContents(each_asset)

                    new_row: list = [
                        row_search,
                        row_name,
                        row_path,
                        True,
                        row_url,
                        each_asset.get('type'),
                        tdVersion,
                        toxVersion,
                        lastSaved,
                        warn,
                        searchMatch,
                        hasCOMPs[0],
                        hasTOPs[0],
                        hasCHOPs[0],
                        hasSOPs[0],
                        hasMATs[0],
                        hasDATs[0]]

                    lister_content.append(new_row)

        for each_row in (rows + lister_content):
            scriptOp.appendRow(each_row)

    except Exception as e:
        print(e)
        print('[~] unable to connect')

    return


def matchContents(asset: dict) -> bool:

    opTypesList: list = asset.get('opTypes')
    opFamilies: list = asset.get('opFamilies')
    termsInputList = opTypesList + opFamilies
    conditionsList = [each.upper() for each in termsInputList]
    conditionsList.append(asset.get('display_name').upper())

    matchList = [
        True if ipar.UIKit.Searchstring.eval().upper() in conditionsList else False for each in conditionsList]

    return any(matchList)
