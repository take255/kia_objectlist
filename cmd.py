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
#ボーンクラスタのリネーム
#チェックを入れたもののみを対象とする
#---------------------------------------------------------------------------------------

#子供を取得
def bone_chain_loop(amt, bone, name, index ):
    #amt = bpy.context.active_object
    for b in amt.data.edit_bones:
        if b.parent == bone:
            b.name = '%s_%02d' % (name , index )
            
            bone_chain_loop(amt, b, name, index + 1 )

def rename_bonecluster():
    props = bpy.context.scene.kiaobjectlist_props
    name = props.rename_string

    ui_list = bpy.context.window_manager.kiaobjectlist_list
    itemlist = ui_list.itemlist    

    amt = utils.getActiveObj()
    parentdic = {}

    rootarray = []
    count = 1
    for node in itemlist:
        if node.bool_val == True:
            b = amt.data.edit_bones[node.name]
            chainname = '%s_%02d' % (name , count )
            rootname = chainname + '_01'
            
            b.name = rootname
            rootarray.append(b.name)
            bone_chain_loop(amt , b, chainname, 2 )
            count += 1
        else:
            rootarray.append(node.name)

    bpy.context.view_layer.update()

    clear()

    for name in rootarray:
        item = itemlist.add()
        item.name = name
        #ui_list.active_index = len(itemlist) - 1


#チェックを入れたものの並びを反転する。
#インデックスを保持したままはめんどいので、ソートしたらリストの末尾に追加
def invert():
    ui_list = bpy.context.window_manager.kiaobjectlist_list
    itemlist = ui_list.itemlist    

    array = []
    indexarray = []
    for i,node in enumerate(itemlist):
        if node.bool_val == True:
            array.append(node.name)
            indexarray.append(i)

    for index in reversed(indexarray):
        itemlist.remove(index)

    for bone in reversed(array):
        item = itemlist.add()
        item.name = bone
        item.bool_val = True
        ui_list.active_index = len(itemlist) - 1

def remove_check_item(op):
    ui_list = bpy.context.window_manager.kiaobjectlist_list
    itemlist = ui_list.itemlist    

    #array = []
    indexarray = []
    for i,node in enumerate(itemlist):
        if op == 'checked':
            if node.bool_val == True:
            #array.append(node.name)
                indexarray.append(i)
        elif op == 'unchecked':
            if node.bool_val == False:
                indexarray.append(i)

    for index in reversed(indexarray):
        itemlist.remove(index)


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


#---------------------------------------------------------------------------------------
#ボーンからクロスメッシュを生成
#揺れジョイント用
#---------------------------------------------------------------------------------------
def bone_chain_loop( bone , chain ,vtxarray ,bonenamearray):
    amt = bpy.context.active_object
    for b in amt.data.edit_bones:
        if b.parent == bone:
            chain.append(b.name)
            bonenamearray.append(b.name)
            vtxarray.append(b.tail)
            bone_chain_loop(b,chain ,vtxarray,bonenamearray)
            

#ジョイントのクラスタからメッシュを作成
#
def create_mesh_from_bone():
    props = bpy.context.scene.kiaobjectlist_props
    ui_list = bpy.context.window_manager.kiaobjectlist_list
    itemlist = ui_list.itemlist    

    amt = bpy.context.object
    #selected = bpy.context.selected_bones
    num_col = 0
    num_row = len(itemlist)


    #頂点座標の配列生成
    #最初のボーンのheadだけの座標を入れれば、残りはtailの座標だけ入れていけばOK
    vtxarray = []

    bonenamearray = []
    chainarray = []

    utils.mode_e()
    for node in itemlist:
        bone = amt.data.edit_bones[node.name]
        chain = [bone.name]
        bonenamearray.append(bone.name)
        vtxarray += [bone.head , bone.tail ]
        bone_chain_loop( bone , chain ,vtxarray ,bonenamearray)
        num_col = len(chain)
        chainarray.append(chain)

    polyarray = []
    ic = num_col + 1 #コラムの増分

    #ポリゴンのインデックス生成
    #円筒状にしたくない場合はrowを１つ減らす
    if props.cloth_open:
        row = num_row -1
    else:
        row = num_row

    for c in range(row):
        array = []
        for r in range(num_col):
            #シリンダ状にループさせたいので、最後のrowは一番目のrowを指定
            if c == num_row - 1:
                array = [
                    r + ic*c ,
                    r + 1 + ic*c ,
                    r + 1  ,
                    r 
                    ]

            else:
                array = [
                    r + ic*c ,
                    r + 1 + ic*c ,
                    r + 1 + ic*(c + 1) ,
                    r + ic*(c + 1)
                    ]

            polyarray.append(array)
    
    #メッシュの生成
    mesh_data = bpy.data.meshes.new("cube_mesh_data")
    mesh_data.from_pydata(vtxarray, [], polyarray)
    mesh_data.update()


    obj = bpy.data.objects.new('test', mesh_data)

    scene = bpy.context.scene
    utils.sceneLink(obj)
    utils.select(obj,True)


    #IKターゲットの頂点グループ作成    
    #ウェイト値の設定
    for j,chain in enumerate(chainarray):
        for i,bone in enumerate(chain):
            obj.vertex_groups.new(name = bone)
            index = 1 + i + j * (num_col+1)

            vg = obj.vertex_groups[bone]
            vg.add( [index], 1.0, 'REPLACE' )


    #IKのセットアップ
    utils.mode_o()
    utils.act(amt)
    utils.mode_p()


    for j,chain in enumerate(chainarray):
        for i,bone in enumerate(chain):

            jnt = amt.pose.bones[bone]
            c = jnt.constraints.new('IK')
            c.target = obj
            c.subtarget = bone
            c.chain_count = 1


    #クロスの設定
    #ピンの頂点グループを設定する
    pin = 'pin'
    obj.vertex_groups.new(name = pin)
    for c in range(num_row):
        index =  c * ( num_col + 1 )
        vg = obj.vertex_groups[pin]
        vg.add( [index], 1.0, 'REPLACE' )


    #bpy.ops.object.modifier_add(type='CLOTH')
    mod = obj.modifiers.new("cloth", 'CLOTH')
    mod.settings.vertex_group_mass = "pin"
