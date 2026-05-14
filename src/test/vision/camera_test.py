import pyzed.sl as sl


print("ZED SDK Version:", sl.Camera.get_sdk_version())

zed = sl.Camera()
init = sl.InitParameters()
init.depth_mode = sl.DEPTH_MODE.NONE   # WYŁĄCZAMY GPU depth
init.sdk_verbose = True

err = zed.open(init)
print("Open result:", err)

zed.close()
