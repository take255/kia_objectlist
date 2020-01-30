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


#オブジェクトモードかエディットモードかを
def add():
    ui_list = bpy.context.window_manager.kiaobjectlist_list
    itemlist = ui_list.itemlist

    mode = utils.current_mode()
    if mode == 'OBJECT':
        for ob in utils.selected():
            item = itemlist.add()
            item.name = ob.name
            ui_list.active_index = len(itemlist) - 1

    elif mode == 'EDIT':
        for bone in utils.get_selected_bones():
            item = itemlist.add()
            item.name = bone.name
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
        if utils.current_mode() == 'OBJECT':
            bpy.ops.object.select_all(action='DESELECT')
        if utils.current_mode() == 'EDIT':
            bpy.ops.armature.select_all(action='DESELECT')

    for node in itemlist:
        if op == 'selected':
            if node.name in obset:
                node.bool_val = True
            else:
                node.bool_val = False

        elif op == 'select':
            if node.bool_val == True:
                #オブジェクトモードなら
                if utils.current_mode() == 'OBJECT':
                    utils.selectByName(node.name,True)

                if utils.current_mode() == 'EDIT':
                    utils.bone.selectByName(node.name,True)

        elif op == 'show':
            if node.bool_val == True:
                utils.showhide(node,False)
 
        elif op == 'hide':
            if node.bool_val == True:
                utils.showhide(node,True)

BoneCount = 0
#---------------------------------------------------------------------------------------
 #オブジェクトの並び替え
#---------------------------------------------------------------------------------------
def reorder():
    global BoneCount
    ui_list = bpy.context.window_manager.kiaobjectlist_list
    itemlist = ui_list.itemlist    

    amt = utils.getActiveObj()
    parentdic = {}


    for node in [x.name for x in itemlist]:
        b = amt.data.edit_bones[node]
        cb = amt.data.edit_bones.new('Bone_duplicated')

        cb.head = b.head
        cb.tail = b.tail
        cb.matrix = b.matrix
        #cb.parent = b


    # bpy.ops.armature.select_all(action='DESELECT')

    # for node in [x.name for x in itemlist]:
    #     parent = amt.data.edit_bones[node].parent
    #     if parent != None:
    #         parentdic[node] = amt.data.edit_bones[node].parent.name
    #         #amt.data.edit_bones[node].parent = None
    #     else:
    #         parentdic[node] = None
        
    #     amt.data.edit_bones[node].select = True

    # bpy.ops.armature.parent_clear(type='CLEAR')
    # bpy.ops.armature.select_all(action='DESELECT')
    
    for node in [x.name for x in itemlist]:
        bpy.ops.armature.select_all(action='DESELECT')
        print(node)
        #amt.data.edit_bones[node].parent = amt.data.edit_bones[parentdic[node]]
        amt.data.edit_bones[node].select = True
        # amt.data.edit_bones[parentdic[node]].select = True
        # amt.data.edit_bones.active = amt.data.edit_bones[parentdic[node]]
        amt.data.edit_bones['Bone'].select = True
        amt.data.edit_bones.active = amt.data.edit_bones['Bone']

        #print(node)
        bpy.ops.armature.parent_set(type='OFFSET')
        
        bpy.context.view_layer.update()



def reorder_():
    ui_list = bpy.context.window_manager.kiaobjectlist_list
    itemlist = ui_list.itemlist    

    amt = utils.getActiveObj()
    parentdic = {}

    bones = []
    for i,node in enumerate([x.name for x in itemlist]):
        print(node)
        #bpy.ops.armature.select_all(action='DESELECT')
        bones.append(amt.data.edit_bones[node])
        # amt.data.edit_bones[node].select = True
        # amt.data.edit_bones.active = amt.data.edit_bones[node]
        # bpy.context.view_layer.update()

        # print(amt.data.edit_bones.active)
        # bpy.ops.armature.duplicate()
    for b in bones:
        b.select= True
        amt.data.edit_bones.active = b
        bpy.ops.armature.duplicate()
    return


    # for node in [x.name for x in itemlist]:
    #     parent = amt.data.edit_bones[node].parent
    #     if parent != None:
    #         parentdic[node] = amt.data.edit_bones[node].parent.name
    #         amt.data.edit_bones[node].parent = None
    #     else:
    #         parentdic[node] = None


    bpy.ops.armature.select_all(action='DESELECT')

    for node in [x.name for x in itemlist]:
        parent = amt.data.edit_bones[node].parent
        if parent != None:
            parentdic[node] = amt.data.edit_bones[node].parent.name
            #amt.data.edit_bones[node].parent = None
        else:
            parentdic[node] = None
        
        amt.data.edit_bones[node].select = True

    bpy.ops.armature.parent_clear(type='CLEAR')



    bpy.ops.armature.select_all(action='DESELECT')
    
    for node in [x.name for x in itemlist]:
        bpy.ops.armature.select_all(action='DESELECT')
        print(node)
        #amt.data.edit_bones[node].parent = amt.data.edit_bones[parentdic[node]]
        amt.data.edit_bones[node].select = True
        amt.data.edit_bones[parentdic[node]].select = True
        amt.data.edit_bones.active = amt.data.edit_bones[parentdic[node]]
        #print(node)
        bpy.ops.armature.parent_set(type='OFFSET')
        
        bpy.context.view_layer.update()
