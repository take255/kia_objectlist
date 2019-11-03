import bpy
from bpy.types import (PropertyGroup , UIList , Operator)
import imp

from . import utils
imp.reload(utils)


#アイテム-------------------------------------------------------
#ItemPropertyはリストのに登録される一つのアイテムを表している

#リストからアイテムを取得
def get_item(self):
    return self["name"]

#リストに選択を登録する
def set_item(self, value):
    self["name"] = value

def showhide(self, value):
    ob = utils.getActiveObj()
    for mod in ob.modifiers :
            if mod.name == self["name"]:
                mod.show_viewport = self["bool_val"]


#---------------------------------------------------------------------------------------
def reload():
    ui_list = bpy.context.window_manager.kiamodifierlist_list
    itemlist = ui_list.itemlist

    clear()
    ob =utils.getActiveObj()

    for mod in ob.modifiers:
        item = itemlist.add()
        item.name = mod.name
        item.bool_val = mod.show_viewport
        ui_list.active_index = len(itemlist) - 1




#---------------------------------------------------------------------------------------
#リストのモディファイヤを探しだし、リストでの順位とモディファイヤの順位を比較する
#その差を出してmove_upで順番を変更する
#---------------------------------------------------------------------------------------
def move(type):
    ui_list = bpy.context.window_manager.kiamodifierlist_list
    itemlist = ui_list.itemlist
    index = ui_list.active_index

    if len(itemlist) < 2:
        return

    if type == 'UP':
        v = index -1
    elif type == 'DOWN':
        v = index + 1
    elif type == 'TOP':
        v = 0
    elif type == 'BOTTOM':
        v = len(itemlist) - 1


    itemlist.move(index, v)
    ui_list.active_index = v

    ob =utils.getActiveObj()

    for order_list,listitem in enumerate(itemlist):
        for order,mod in enumerate(ob.modifiers):
            
            if mod.name == listitem.name:
                if (order_list < order):
                    for i in range(order - order_list):
                        bpy.ops.object.modifier_move_up(modifier = mod.name )




def select_all():
    ui_list = bpy.context.window_manager.kiaobjectlist_list
    itemlist = ui_list.itemlist

    if len(itemlist) == 0:
        return {"FINISHED"}
    
    for node in itemlist:
        utils.selectByName( node.name,True )
        #bpy.data.objects[node.name].select = True


def add():
    ui_list = bpy.context.window_manager.kiaobjectlist_list
    itemlist = ui_list.itemlist

    for ob in utils.selected():
        item = itemlist.add()
        item.name = ob.name
        ui_list.active_index = len(itemlist) - 1


def remove():
    ui_list = bpy.context.window_manager.kiaobjectlist_list
    itemlist = ui_list.itemlist

    if len(itemlist):
        itemlist.remove(ui_list.active_index)
        if len(itemlist)-1 < ui_list.active_index:
            ui_list.active_index = len(itemlist)-1
            if ui_list.active_index < 0:
                ui_list.active_index = 0


def remove_not_exist():
    ui_list = bpy.context.window_manager.kiaobjectlist_list
    itemlist = ui_list.itemlist
    index = ui_list.active_index

    if len(itemlist) == 0:
        return

    result = []
    for node in itemlist:
        if node.name in bpy.data.objects:
            print(node.name)
            result.append(node.name)
    
    itemlist.clear()

    for nodename in result:
        item = itemlist.add()
        item.name = nodename
        index = len(itemlist)-1


def move(dir):
    ui_list = bpy.context.window_manager.kiaobjectlist_list
    itemlist = ui_list.itemlist
    index = ui_list.active_index

    if len(itemlist) < 2:
        return

    if dir == 'UP':
        v = index -1
    elif dir == 'DOWN':
        v = index + 1

    itemlist.move(index, v)
    ui_list.active_index = v


def clear():
    ui_list = bpy.context.window_manager.kiaobjectlist_list
    itemlist = ui_list.itemlist    
    itemlist.clear()


#---------------------------------------------------------------------------------------
#チェックを入れたオブジェクトに関しての操作
#---------------------------------------------------------------------------------------
def check_item(op):
    ui_list = bpy.context.window_manager.kiaobjectlist_list
    itemlist = ui_list.itemlist    

    if len(itemlist) == 0:
        return

    obset = set([ob.name for ob in bpy.context.selected_objects])
    if op == 'select':
        bpy.ops.object.select_all(action='DESELECT')

    for node in itemlist:
        if op == 'selected':
            if node.name in obset:
                node.bool_val = True
            else:
                node.bool_val = False

        elif op == 'select':
            if node.bool_val == True:
                utils.selectByName(node.name,True)

        elif op == 'show':
            if node.bool_val == True:
                utils.showhide(node,False)
 
        elif op == 'hide':
            if node.bool_val == True:
                utils.showhide(node,True)
 