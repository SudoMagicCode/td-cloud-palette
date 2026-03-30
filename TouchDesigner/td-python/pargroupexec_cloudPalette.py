"""
ParGroup Execute DAT

me - this DAT

cur - the Par object that has changed
prev - the previous value (or a list of previous values)

NOTE: If Callback Mode is set to 'Combine ParGroup Changes as List',
both cur and prev are instead lists.
NOTE: Make sure the corresponding toggle is enabled in the ParGroup
Execute DAT.
"""

from typing import Any, Union, List


def onValueChange(cur: Union[Par, List[Par]],
                  prev: Union[Any, List[Any]]):
    """
    Called when parameter values change.

    Args:
            cur: The Par object(s) that changed (use cur.eval() to get current)
            prev: The previous value(s)
    """
    # use cur.eval() to get current
    return


def onExpressionChange(cur: Union[Any, List[Any]],
                       prev: Union[Any, List[Any]]):
    """
    Called when parameter expressions change.

    Args:
            cur: The current expression(s) (use cur.expr to get current)
            prev: The previous expression(s)
    """
    # use cur.expr to get current
    return


def onExportChange(cur: Union[Any, List[Any]],
                   prev: Union[Any, List[Any]]):
    """
    Called when parameter exports change.

    Args:
            cur: The current export(s) (use cur.exportSource to get current)
            prev: The previous export(s)
    """
    # use cur.exportSource to get current
    return


def onEnableChange(cur: Union[Any, List[Any]],
                   prev: Union[Any, List[Any]]):
    """
    Called when parameter enable states change.

    Args:
            cur: The current enable state(s) (use cur.enable to get current)
            prev: The previous enable state(s)
    """
    # use cur.enable to get current
    return


def onModeChange(cur: Union[Any, List[Any]],
                 prev: Union[Any, List[Any]]):
    """
    Called when parameter modes change.

    Args:
            cur: The current mode(s) (use cur.mode to get current)
            prev: The previous mode(s)
    """
    # use cur.mode to get current
    return


def onPulse(cur: Union[Any, List[Any]]):
    """
    Called when parameters are pulsed.

    Args:
            cur: The parameter(s) that were pulsed
    """
    match cur.name:
        case 'Loadinventory':
            parent().Load_inventory()
        case 'Buildlocalcache':
            parent().Download_tox_files()
        case 'Deletelocalcache':
            parent().Delete_local_cache()
        case 'Update':
            parent().Update_tox()
        case 'Refresh':
            parent().Refresh_inventory()
        case _:
            print(cur.name)

    return
