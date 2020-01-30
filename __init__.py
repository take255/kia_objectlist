# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


import bpy
from bpy.app.handlers import persistent
import imp

from bpy.types import( 
    PropertyGroup,
    Panel,
    Operator,
    UIList,
    AddonPreferences
    )

from bpy.props import(
    PointerProperty,
    IntProperty,
    BoolProperty,
    StringProperty,
    CollectionProperty
    )

from . import utils
from . import cmd

imp.reload(utils)
imp.reload(cmd)


bl_info = {
"name": "kiaobjectlist",
"author": "kisekiakeshi",
"version": (0, 1),
"blender": (2, 80, 0),
"description": "kiaobjectlist",
"category": "Object"}


try: 
    bpy.utils.unregister_class(KIAOBJECTLIST_Props_item)
except:
    pass

#リストでアイテムを選択したときオブジェクトを選択する
@persistent
def kiaobjectlist_handler(scene):
    ui_list = bpy.context.window_manager.kiaobjectlist_list
    itemlist = ui_list.itemlist
    props = bpy.context.scene.kiaobjectlist_props

    #インデックスが変わったときだけ選択
    if len(itemlist) > 0:
        index = ui_list.active_index
        if props.currentindex != index:
            props.currentindex = index#先に実行しておかないとdeselectでhandlerがループしてしまう

            mode = utils.current_mode()
            if mode == 'OBJECT':
                bpy.ops.object.select_all(action='DESELECT')
                utils.selectByName(itemlist[index].name,True)

            if mode == 'EDIT':
                bpy.ops.armature.select_all(action='DESELECT')
                utils.bone.selectByName(itemlist[index].name,True)

                #bpy.ops.object.select_all(action='DESELECT')
                #utils.selectByName(itemlist[index].name,True)


class KIAOBJECTLIST_Props_OA(PropertyGroup):
    currentindex : IntProperty()

#---------------------------------------------------------------------------------------
#リスト内のアイテムの見た目を指定
#---------------------------------------------------------------------------------------
class KIAOBJECTLIST_UL_uilist(UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:

            #item.nameが表示される
            layout.prop(item, "bool_val", text = "")
            layout.prop(item, "name", text="", emboss=False, icon_value=icon)

        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


#---------------------------------------------------------------------------------------
#リスト名 , list_id can be ””　，item_ptr ,item , index_pointer ,active_index
#active_indexをui_list.active_indexで取得できる
#---------------------------------------------------------------------------------------
class KIAOBJECTLIST_PT_ui(utils.panel):
    bl_label = "kia_objectlist"

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout=self.layout
        row = layout.row()

        col = row.column()
        ui_list = context.window_manager.kiaobjectlist_list

        col.template_list("KIAOBJECTLIST_UL_uilist", "", ui_list, "itemlist", ui_list, "active_index", rows=8)
        col = row.column(align=True)

        col.operator("kiaobjectlist.select_all", icon='PROP_CON')
        col.operator("kiaobjectlist.add", icon=utils.icon['ADD'])
        col.operator("kiaobjectlist.remove", icon=utils.icon['REMOVE'])
        col.operator("kiaobjectlist.move_item", icon=utils.icon['UP']).dir = 'UP'
        col.operator("kiaobjectlist.move_item", icon=utils.icon['DOWN']).dir = 'DOWN'
        col.operator("kiaobjectlist.clear", icon=utils.icon['CANCEL'])
        col.operator("kiaobjectlist.remove_not_exist", icon='ERROR')

        row = layout.row(align=True)
        row.label( text = 'check' )
        for x in ('show' , 'hide' , 'select' , 'selected'):
            row.operator("kiaobjectlist.check_item", text = x ).op = x

        row = layout.row(align=True)
        row.label( text = 'check' )
        row.operator("kiaobjectlist.reorder")
        
        

#---------------------------------------------------------------------------------------
#リストのアイテムに他の情報を埋め込みたい場合はプロパティを追加できるのでいろいろ追加してみよう。
#ここでレジストしないと不具合がでる。register()に含めたいところだが。
#TestCollectionPropertyのitemListの型として指定する必要があるので後でレジストできない
#---------------------------------------------------------------------------------------

class KIAOBJECTLIST_Props_item(PropertyGroup):
    name : StringProperty(get=cmd.get_item, set=cmd.set_item)
    bool_val : BoolProperty( update = cmd.showhide )

bpy.utils.register_class(KIAOBJECTLIST_Props_item)


#---------------------------------------------------------------------------------------
#アイテムのリストクラス
#複数のアイテムをリストに持ち、リストにアイテムを加えたり、選択したリストを取得したりする。
#このクラス自体はuiをもっているわけではないので、現在リストで選択されているインデックスを取得する必要がある。
#
#col.template_list("Modifierlist_group_list", "", ui_list, "itemlist", ui_list, "active_index", rows=3)
#template_listで選択されたアイテムのインデックスをactive_indexに渡すため、上のように指定する必要がある。

#CollectionPropertyへの追加方法例
# item = self.list.add()
# item.name = bone.name
# item.int_val = 10
#---------------------------------------------------------------------------------------
class KIAOBJECTLIST_Props_list(PropertyGroup):
    active_index : IntProperty()
    itemlist : CollectionProperty(type=KIAOBJECTLIST_Props_item)#アイテムプロパティの型を収めることができるリストを生成

class KIAOBJECTLIST_OT_select_all(Operator):
    """全選択"""
    bl_idname = "kiaobjectlist.select_all"
    bl_label = ""
    def execute(self, context):
        cmd.select_all()
        return {'FINISHED'}

class KIAOBJECTLIST_OT_add(Operator):
    """選択を追加"""
    bl_idname = "kiaobjectlist.add"
    bl_label = ""
    def execute(self, context):
        cmd.add()
        return {'FINISHED'}

class KIAOBJECTLIST_OT_remove(Operator):
    """選択を削除"""
    bl_idname = "kiaobjectlist.remove"
    bl_label = ""

    def execute(self, context):
        cmd.remove()
        return {'FINISHED'}

class KIAOBJECTLIST_OT_remove_not_exist(Operator):
    """存在していないものを削除"""
    bl_idname = "kiaobjectlist.remove_not_exist"
    bl_label = ""
    def execute(self, context):
        cmd.remove_not_exist()
        return {'FINISHED'}

class KIAOBJECTLIST_OT_move_item(Operator):
    """アイテムの移動"""
    bl_idname = "kiaobjectlist.move_item"
    bl_label = ""
    dir : StringProperty(default='UP')

    def execute(self, context):
        cmd.move(self.dir)
        return {'FINISHED'}

class KIAOBJECTLIST_OT_clear(Operator):
    """アイテムのクリア"""
    bl_idname = "kiaobjectlist.clear"
    bl_label = ""
    def execute(self, context):
        cmd.clear()
        return {'FINISHED'}


class KIAOBJECTLIST_OT_check_item(Operator):
    """アイテムの移動"""
    bl_idname = "kiaobjectlist.check_item"
    bl_label = ""
    op : StringProperty()

    def execute(self, context):
        cmd.check_item(self.op)
        return {'FINISHED'}


#アイテムのオーダーをリストの通りにする。
class KIAOBJECTLIST_OT_reorder(Operator):
    """アイテムのクリア"""
    bl_idname = "kiaobjectlist.reorder"
    bl_label = "reorder"
    def execute(self, context):
        cmd.reorder()
        return {'FINISHED'}



classes = (
    KIAOBJECTLIST_Props_OA,
    KIAOBJECTLIST_UL_uilist,
    KIAOBJECTLIST_PT_ui,
    KIAOBJECTLIST_Props_list,    


    KIAOBJECTLIST_OT_select_all,
    KIAOBJECTLIST_OT_add,
    KIAOBJECTLIST_OT_remove,
    KIAOBJECTLIST_OT_remove_not_exist,
    KIAOBJECTLIST_OT_move_item,
    KIAOBJECTLIST_OT_clear,

    KIAOBJECTLIST_OT_check_item,

    KIAOBJECTLIST_OT_reorder

)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.kiaobjectlist_props = PointerProperty(type=KIAOBJECTLIST_Props_OA)
    bpy.types.WindowManager.kiaobjectlist_list = PointerProperty(type=KIAOBJECTLIST_Props_list)
    bpy.app.handlers.depsgraph_update_pre.append(kiaobjectlist_handler)



def unregister():
    
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.kiaobjectlist_props
    del bpy.types.WindowManager.kiaobjectlist_list
    bpy.app.handlers.depsgraph_update_pre.remove(kiaobjectlist_handler)

