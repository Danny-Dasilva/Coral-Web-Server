import cairo
import contextlib
import ctypes

import gi
gi.require_version('Gdk', '3.0')
gi.require_version('GObject', '2.0')
gi.require_version('Gst', '1.0')
gi.require_version('GstBase', '1.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import Gdk, GObject, Gst, GstBase, GstVideo

Gdk.init([])

# Gst.Buffer.map(Gst.MapFlags.WRITE) is broken, this is a workaround. See
# http://lifestyletransfer.com/how-to-make-gstreamer-buffer-writable-in-python/
# https://gitlab.gnome.org/GNOME/gobject-introspection/issues/69
class GstMapInfo(ctypes.Structure):
    _fields_ = [('memory', ctypes.c_void_p),                # GstMemory *memory
                ('flags', ctypes.c_int),                    # GstMapFlags flags
                ('data', ctypes.POINTER(ctypes.c_byte)),    # guint8 *data
                ('size', ctypes.c_size_t),                  # gsize size
                ('maxsize', ctypes.c_size_t),               # gsize maxsize
                ('user_data', ctypes.c_void_p * 4),         # gpointer user_data[4]
                ('_gst_reserved', ctypes.c_void_p * 4)]     # GST_PADDING

# ctypes imports for missing or broken introspection APIs.
libgst = ctypes.CDLL('libgstreamer-1.0.so.0')
libgst.gst_context_writable_structure.restype = ctypes.c_void_p
libgst.gst_context_writable_structure.argtypes = [ctypes.c_void_p]
libgst.gst_structure_set.restype = ctypes.c_void_p
libgst.gst_structure_set.argtypes = [ctypes.c_void_p, ctypes.c_char_p,
        ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p]
GST_MAP_INFO_POINTER = ctypes.POINTER(GstMapInfo)
libgst.gst_buffer_map.argtypes = [ctypes.c_void_p, GST_MAP_INFO_POINTER, ctypes.c_int]
libgst.gst_buffer_map.restype = ctypes.c_int
libgst.gst_buffer_unmap.argtypes = [ctypes.c_void_p, GST_MAP_INFO_POINTER]
libgst.gst_buffer_unmap.restype = None
libgst.gst_mini_object_is_writable.argtypes = [ctypes.c_void_p]
libgst.gst_mini_object_is_writable.restype = ctypes.c_int

libgdk = ctypes.CDLL('libgdk-3.so.0')
libgdk.gdk_wayland_window_get_wl_surface.restype = ctypes.c_void_p
libgdk.gdk_wayland_window_get_wl_surface.argtypes = [ctypes.c_void_p]
libgdk.gdk_wayland_display_get_wl_display.restype = ctypes.c_void_p
libgdk.gdk_wayland_display_get_wl_display.argtypes = [ctypes.c_void_p]

libcairo = ctypes.CDLL('libcairo.so.2')
libcairo.cairo_image_surface_create_for_data.restype = ctypes.c_void_p
libcairo.cairo_image_surface_create_for_data.argtypes = [ctypes.c_void_p,
        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
libcairo.cairo_surface_flush.restype = None
libcairo.cairo_surface_flush.argtypes = [ctypes.c_void_p]
libcairo.cairo_surface_destroy.restype = None
libcairo.cairo_surface_destroy.argtypes = [ctypes.c_void_p]
libcairo.cairo_surface_status.restype = ctypes.c_int
libcairo.cairo_surface_status.argtypes = [ctypes.c_void_p]
libcairo.cairo_format_stride_for_width.restype = ctypes.c_int
libcairo.cairo_format_stride_for_width.argtypes = [ctypes.c_int, ctypes.c_int]
libcairo.cairo_create.restype = ctypes.c_void_p
libcairo.cairo_create.argtypes = [ctypes.c_void_p]
libcairo.cairo_destroy.restype = None
libcairo.cairo_destroy.argtypes = [ctypes.c_void_p]
libcairo.cairo_scale.restype = None
libcairo.cairo_scale.argtypes = [ctypes.c_void_p, ctypes.c_double, ctypes.c_double]

librsvg = ctypes.CDLL('librsvg-2.so.2')
librsvg.rsvg_handle_new_from_data.restype = ctypes.c_void_p
librsvg.rsvg_handle_new_from_data.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_void_p]
librsvg.rsvg_handle_render_cairo.restype = ctypes.c_bool
librsvg.rsvg_handle_render_cairo.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
librsvg.rsvg_handle_close.restype = ctypes.c_bool
librsvg.rsvg_handle_close.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

libgobject = ctypes.CDLL('libgobject-2.0.so.0')
libgobject.g_object_unref.restype = None
libgobject.g_object_unref.argtypes = [ctypes.c_void_p]

def set_display_contexts(sink, widget):
    handle = libgdk.gdk_wayland_window_get_wl_surface(hash(widget.get_window()))
    sink.set_window_handle(handle)

    wl_display = libgdk.gdk_wayland_display_get_wl_display(hash(Gdk.Display.get_default()))
    context = Gst.Context.new('GstWaylandDisplayHandleContextType', True)
    structure = libgst.gst_context_writable_structure(hash(context))
    libgst.gst_structure_set(structure, ctypes.c_char_p('display'.encode()),
            hash(GObject.TYPE_POINTER), wl_display, 0)
    sink.set_context(context)

@contextlib.contextmanager
def _gst_buffer_map(buffer, flags):
    ptr = hash(buffer)
    if flags & Gst.MapFlags.WRITE and libgst.gst_mini_object_is_writable(ptr) == 0:
        raise ValueError('Buffer not writable')

    mapping = GstMapInfo()
    success = libgst.gst_buffer_map(ptr, mapping, flags)
    if not success:
        raise RuntimeError('gst_buffer_map failed')
    try:
        yield ctypes.cast(mapping.data, ctypes.POINTER(ctypes.c_byte * mapping.size)).contents
    finally:
        libgst.gst_buffer_unmap(ptr, mapping)

