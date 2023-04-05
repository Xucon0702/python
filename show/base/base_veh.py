#宏定义

veh_type = "A58"

if(veh_type == "A58"):
    print("veh is A58")
    #GAC_A58车车身参数,单位/m
    AXIS_DISTANCE  = 2.730
    VEHICLE_LEN	= 4.650
    VEHICLE_WID	= 1.887
    FRONT_EDGE2CENTER = 3.674
    REAR_EDGE2CENTER  = 0.976
    SIDE_EDGE2CENTER  = VEHICLE_WID / 2
    WHEEL_BASE        = AXIS_DISTANCE
else:
    print("unknow veh type")



class C_base_veh:
    # def __init__(self,xx,yy):
    #     self.x=xx
    #     self.y=yy

    def CalCornerCoordinate():
        print("AXIS_DISTANCE: ",AXIS_DISTANCE)
        return

    


#ifdef A58

#endif