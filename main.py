import c4d
from c4d import gui, bitmaps, documents, utils
import os, sys
import math
import webbrowser
import json


try:
    from mxutils import LocalImportPath
    with LocalImportPath(__file__):
        import requests
except: # older c4d
    deps_dir = os.path.join(os.path.dirname(__file__), "dependencies")
    if deps_dir not in sys.path:
        sys.path.insert(0, deps_dir)

    import requests

PLUGIN_PATH = os.path.dirname(__file__)
if PLUGIN_PATH not in sys.path:
    sys.path.insert(0, PLUGIN_PATH)


PLUGIN_ID = 1065724
DIALOG_ID = 2065724

# GUI element IDs
IDC_POSE_DROPDOWN = 20000
IDC_FKIK_CHECKBOX = 20001
IDC_IMPORT_ARMATURE = 20002
IDC_ADD_POSE = 20003
IDC_POSES_SCROLL = 20004
IDC_POSES_CONTAINER = 20005
IDC_TOTAL_FRAMES = 20006
IDC_FPS = 20007
IDC_IS_LOOPING = 20008
IDC_SOLVE_IK = 20009
IDC_GENERATE_ANIMATION = 20010
IDC_FETCH_ANIMATION = 20011
IDC_API_KEY = 20012
IDC_LOGO_BITMAP = 20013

IDC_POSE_REMOVE_BASE     = 21000
IDC_POSE_COMBO_BASE      = 22000
IDC_POSE_STATIC_BASE     = 23000
IDC_POSE_STATIC_LABEL_BASE = 24000
IDC_POSE_FRAME_LABEL_BASE= 25000
IDC_POSE_FRAME_FIELD_BASE= 26000


# Anym consts
HEADER = """
HIERARCHY
ROOT AnymHips
{
    OFFSET 0.000000 0.000000 0.000000
    CHANNELS 6 Xposition Yposition Zposition Zrotation Yrotation Xrotation
    JOINT AnymLeftHip
    {
        OFFSET 0.080781 0.005359 -0.054022
        CHANNELS 3 Zrotation Yrotation Xrotation
        JOINT AnymLeftKnee
        {
            OFFSET 0.000000 -0.010000 -0.417793
            CHANNELS 3 Zrotation Yrotation Xrotation
            JOINT AnymLeftFoot
            {
                OFFSET 0.000000 0.000000 -0.401472
                CHANNELS 3 Zrotation Yrotation Xrotation
                JOINT AnymLeftToe
                {
                    OFFSET 0.011334 -0.104165 -0.041164
                    CHANNELS 3 Zrotation Yrotation Xrotation
                    End Site
                    {
                        OFFSET 0.000000 -0.150000 0.000000
                    }
                }
            }
        }
    }
    JOINT AnymRightHip
    {
        OFFSET -0.080781 0.005359 -0.054025
        CHANNELS 3 Zrotation Yrotation Xrotation
        JOINT AnymRightKnee
        {
            OFFSET 0.000000 -0.010000 -0.417793
            CHANNELS 3 Zrotation Yrotation Xrotation
            JOINT AnymRightFoot
            {
                OFFSET 0.000000 0.000000 -0.401472
                CHANNELS 3 Zrotation Yrotation Xrotation
                JOINT AnymRightToe
                {
                    OFFSET  -0.011334 -0.104165 -0.041168
                    CHANNELS 3 Zrotation Yrotation Xrotation
                    End Site
                    {
                        OFFSET 0.000000 -0.150000 0.000000
                    }
                }
            }
        }
    }
    JOINT AnymSpine
    {
        OFFSET 0.000000 0.011802 0.097172
        CHANNELS 3 Zrotation Yrotation Xrotation
        JOINT AnymSpine1
        {
            OFFSET 0.000000 0.013769 0.113368
            CHANNELS 3 Zrotation Yrotation Xrotation
            JOINT AnymSpine2
            {
                OFFSET 0.000000 0.015737 0.129563
                CHANNELS 3 Zrotation Yrotation Xrotation
                JOINT AnymNeck
                {
                    OFFSET 0.000000 0.017704 0.145760
                    CHANNELS 3 Zrotation Yrotation Xrotation
                    JOINT AnymHead
                    {
                        OFFSET  0.000000 -0.019722 0.067202
                        CHANNELS 3 Zrotation Yrotation Xrotation
                        End Site
                        {
                            OFFSET 0.000000 0.000000 0.200000
                        }
                    }
                }
                JOINT AnymLeftShoulder
                {
                    OFFSET 0.061401 0.017995 0.098779
                    CHANNELS 3 Zrotation Yrotation Xrotation
                    JOINT AnymLeftArm
                    {
                        OFFSET 0.115589 0.000581 0.000000
                        CHANNELS 3 Zrotation Yrotation Xrotation
                        JOINT AnymLeftForearm
                        {
                            OFFSET 0.255608 0.010000 0.000000
                            CHANNELS 3 Zrotation Yrotation Xrotation
                            JOINT AnymLeftHand
                            {
                                OFFSET 0.234041 -0.010000 0.00000
                                CHANNELS 3 Zrotation Yrotation Xrotation
                                End Site
                                {
                                    OFFSET 0.200000 0.000000 0.000000
                                }
                            }
                        }
                    }
                }
                JOINT AnymRightShoulder
                {
                    OFFSET -0.061401 0.017414 0.098778
                    CHANNELS 3 Zrotation Yrotation Xrotation
                    JOINT AnymRightArm
                    {
                        OFFSET -0.115589 -0.000581 0.000000
                        CHANNELS 3 Zrotation Yrotation Xrotation
                        JOINT AnymRightForearm
                        {
                            OFFSET -0.255711 0.010000 0.000000
                            CHANNELS 3 Zrotation Yrotation Xrotation
                            JOINT AnymRightHand
                            {
                                OFFSET -0.234017 -0.010000 0.000000
                                CHANNELS 3 Zrotation Yrotation Xrotation
                                End Site
                                {
                                    OFFSET -0.200000 0.000000 0.000000
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
MOTION
Frames: 1
Frame Time: 0.050000
"""


ANYM_POSES = {
    'tpose': '0.0 0.0 0.91 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0',
    'standing': '0.0 0.0 0.915556 -2.686633 -2.507240 -3.725996 8.863924 -0.977226 1.382313 0.000000 0.113183 10.036398 2.418233 -4.287297 -4.288259 0.000000 0.000000 -0.000001 0.968358 5.593504 0.122170 0.435359 -0.016123 8.599061 -5.051244 -1.822243 -5.085787 0.000000 0.000000 -0.000001 0.807181 4.508004 -1.114769 -3.923263 -1.782650 11.946513 -2.286621 0.419885 -1.593431 5.200063 -3.178905 -5.355329 -1.712830 1.747785 16.304016 -1.668256 9.644320 4.197483 -3.659436 71.470565 5.343645 -32.365001 -8.193753 17.004270 -8.932759 7.274603 17.997885 4.799549 -14.141005 0.980003 14.342044 -67.479631 0.540239 24.710453 10.176975 12.695284 5.134529 -5.652613 22.329369\n',
    'walking': '0.0 0.0 0.869634 -5.156413 -1.214391 -5.410411 -1.709857 2.046793 -20.518447 -0.194409 2.821928 9.639633 22.674375 2.022817 7.065949 0.319114 -0.242817 -0.046777 -0.485952 -0.883780 21.276853 12.540215 -1.923606 17.813456 -12.848437 -5.769769 -8.659176 -0.403757 0.317752 -0.080174 4.731687 0.752432 14.091849 -1.918952 0.502233 1.095741 1.762074 0.605030 1.362915 -1.460636 4.213001 -19.982780 -0.953491 -5.442693 5.160420 5.932315 5.130612 1.747537 18.007731 72.350556 25.328865 -31.373172 -5.726233 -2.154197 2.176981 19.996316 -18.105757 1.457258 -5.002118 -1.150550 23.709883 -64.830696 -12.471515 41.735666 7.170822 -5.860969 -0.917491 -16.211826 -11.683631\n',
    'running': '0.0 0.0 0.944308 12.812485 -3.764145 -3.449099 6.162934 -2.591651 21.884037 -16.779459 5.769927 1.611377 12.924832 2.332486 2.128104 0.000000 0.000000 -0.000001 2.281804 7.332328 -16.747847 -10.971671 -0.227808 8.013506 -23.763674 -7.757531 -2.377268 0.000000 0.000000 -0.000001 -10.430504 6.608937 6.446684 -10.014379 -4.599386 6.985147 -10.106457 -0.428153 2.249650 8.424983 -2.053782 -10.427315 2.427841 1.754064 0.686918 -6.744412 -1.306699 4.014442 -37.160491 65.066568 -17.400981 -107.616498 0.533386 23.300145 -20.239555 -7.541115 -2.493251 -8.147590 2.082604 4.206349 -35.837155 -62.851323 58.385568 113.784891 1.138298 20.943669 23.422029 -4.067571 -27.872150\n',
    'crouched': '0.0 0.0 0.792000 -7.587353 -3.244431 -5.244226 10.449458 -2.692427 1.237742 8.725213 8.053955 59.866197 28.034230 4.273684 -27.513477 -0.000001 -0.000000 0.000000 -12.310561 4.514536 -49.888928 -24.246104 5.546499 49.671887 -30.678573 9.327886 5.286487 0.000001 0.000000 0.000000 -8.409343 1.527181 46.302820 -4.850420 0.085146 10.987337 -3.818213 -0.937031 2.779952 15.485148 4.624125 9.982532 6.171311 -0.166689 -33.296183 -22.539460 -6.687543 -7.196572 -42.859961 27.952473 -40.464302 -95.768290 -24.000663 9.008869 -17.402181 -4.216924 19.540276 20.828827 7.671515 -3.644733 22.885188 -70.705963 -26.571569 73.503613 7.590814 9.765324 12.214401 -0.851391 0.037118\n',
    'fighting': '0.0 0.0 0.929197 1.998556 0.365758 -2.714235 11.078149 -15.233524 -13.417147 15.345969 0.333671 13.138032 12.556353 10.035754 18.094387 0.000000 0.000000 -0.000001 -7.943415 11.946518 7.718570 -9.117149 -5.011846 5.266846 -16.635733 -4.257653 0.560239 0.000000 0.000000 -0.000001 0.645713 -0.742055 11.902913 3.841259 2.161500 -1.203929 0.955819 0.166722 -0.892026 12.257349 -0.606808 2.459871 15.515777 3.088477 13.207125 -10.436967 -19.768036 -9.090913 -52.863180 56.077539 -40.028783 -112.513607 -29.267658 25.987605 -6.362055 -16.723496 -3.005818 13.895320 20.171606 -7.156372 83.480282 -55.718614 -57.387083 110.505613 0.414810 22.901932 13.447608 21.708462 -25.038953\n',
}

BVH_JOINT_ORDER = [
    "AnymHips",
    "AnymLeftHip", "AnymLeftKnee", "AnymLeftFoot", "AnymLeftToe",
    "AnymRightHip", "AnymRightKnee", "AnymRightFoot", "AnymRightToe",
    "AnymSpine", "AnymSpine1", "AnymSpine2", "AnymNeck", "AnymHead",
    "AnymLeftShoulder", "AnymLeftArm", "AnymLeftForearm", "AnymLeftHand",
    "AnymRightShoulder", "AnymRightArm", "AnymRightForearm", "AnymRightHand"
]


class BVHJointData:
    def __init__(self, name, parent_data=None, is_end_site=False):
        self.name = name
        self.parent = parent_data
        self.offset = c4d.Vector(0)
        self.channels = []
        self.children = []
        self.is_end_site = is_end_site
        self.c4d_object = None

def parse_bvh_data(lines, scale=100):
    """
    Parses the HIERARCHY and MOTION sections of a BVH file.

    Args:
        lines (list[str]): A list of strings, where each string is a line from the BVH file.

    Returns:
        tuple: (root_bvh_joint, all_bvh_joints, ordered_channels_for_motion, frame_values)
            - root_bvh_joint (BVHJointData): The root joint's data.
            - all_bvh_joints (dict): A dictionary mapping joint names to BVHJointData objects.
            - ordered_channels_for_motion (list[tuple]): A list of (joint_name, channel_type)
              tuples in the exact order they appear in the MOTION section's frame data.
            - frame_values (list[float]): A list of floating-point values from the single frame.

    Raises:
        ValueError: If essential sections are missing or parsing errors occur.
    """
    # --- HIERARCHY Parsing ---
    hierarchy_start_idx = -1
    for i, line in enumerate(lines):
        if line.strip() == "HIERARCHY":
            hierarchy_start_idx = i
            break
    if hierarchy_start_idx == -1:
        raise ValueError("HIERARCHY section not found.")

    all_bvh_joints = {}
    root_bvh_joint = None
    current_parent_stack = []  # Stack of BVHJointData objects to manage hierarchy nesting
    ordered_channels_for_motion = [] # Stores (joint_name, channel_type) in motion data order

    line_idx = hierarchy_start_idx + 1
    while line_idx < len(lines):
        line = lines[line_idx].strip()
        line_idx += 1

        if not line: continue # Skip empty lines
        if line == "MOTION": break # End of HIERARCHY section

        parts = line.split()
        if not parts: continue # Skip empty lines after split

        if parts[0] == "ROOT" or parts[0] == "JOINT":
            joint_name = " ".join(parts[1:])
            parent_joint_data = current_parent_stack[-1] if current_parent_stack else None
            joint_data = BVHJointData(joint_name, parent_joint_data)
            all_bvh_joints[joint_name] = joint_data

            if parent_joint_data:
                parent_joint_data.children.append(joint_data)
            if parts[0] == "ROOT":
                root_bvh_joint = joint_data
            
            # Expect '{' on the next line to open the joint's definition block
            if line_idx >= len(lines) or lines[line_idx].strip() != "{":
                raise ValueError(f"Expected '{{' after {parts[0]} {joint_name} definition.")
            line_idx += 1 # Consume '{'
            current_parent_stack.append(joint_data) # Push current joint onto the stack

        elif parts[0] == "OFFSET":
            if not current_parent_stack:
                raise ValueError("OFFSET keyword found without an active joint in the hierarchy stack.")
            current_joint_data = current_parent_stack[-1]
            current_joint_data.offset = current_joint_data.offset = c4d.Vector(
                float(parts[1]) * scale,
                float(parts[2]) * scale,
                -float(parts[3]) * scale,
            )

        elif parts[0] == "CHANNELS":
            if not current_parent_stack:
                raise ValueError("CHANNELS keyword found without an active joint in the hierarchy stack.")
            current_joint_data = current_parent_stack[-1]
            num_channels = int(parts[1])
            current_joint_data.channels = parts[2:2+num_channels]
            # Record the channel order for later parsing of motion data
            for channel_type in current_joint_data.channels:
                ordered_channels_for_motion.append((current_joint_data.name, channel_type))

        elif parts[0] == "End" and parts[1] == "Site":
            # An End Site is a special type of joint that usually only has an offset
            # and signifies the end of a bone chain.
            if not current_parent_stack:
                raise ValueError("End Site found without a parent joint in the hierarchy stack.")
            
            end_site_name = current_parent_stack[-1].name + "_EndSite" # Create a unique name
            parent_joint_data = current_parent_stack[-1]
            end_site_data = BVHJointData(end_site_name, parent_joint_data, is_end_site=True)
            all_bvh_joints[end_site_name] = end_site_data
            parent_joint_data.children.append(end_site_data)

            # Expect '{' on the next line for End Site definition
            if line_idx >= len(lines) or lines[line_idx].strip() != "{":
                raise ValueError(f"Expected '{{' after End Site {end_site_name} definition.")
            line_idx += 1 # Consume '{'
            
            # Expect OFFSET on the next line for End Site
            if line_idx >= len(lines): raise ValueError("Unexpected end of file after End Site '{'.")
            offset_parts = lines[line_idx].strip().split()
            line_idx += 1
            if offset_parts[0] != "OFFSET": raise ValueError(f"Expected OFFSET for End Site {end_site_name}.")
            end_site_data.offset = current_joint_data.offset = c4d.Vector(
                float(offset_parts[1]) * scale,
                float(offset_parts[2]) * scale,
                -float(offset_parts[3]) * scale
            )

            # Expect '}' on the next line for End Site
            if line_idx >= len(lines) or lines[line_idx].strip() != "}":
                raise ValueError(f"Expected '}}' after End Site OFFSET {end_site_name}.")
            line_idx += 1 # Consume '}'
            # End Sites do not push to the stack as they don't contain further nested hierarchy

        elif parts[0] == "}":
            # Closing bracket for a joint definition block
            if current_parent_stack:
                current_parent_stack.pop()
            else:
                # If stack is empty and we encounter '}', it likely closes the root block.
                # The next line should typically be "MOTION".
                if line_idx < len(lines) and lines[line_idx].strip() == "MOTION":
                    break # Successfully parsed hierarchy, move to MOTION

    if not root_bvh_joint:
        raise ValueError("Root joint not found after HIERARCHY parsing.")

    # --- MOTION Parsing ---
    motion_start_idx = -1
    # Search for MOTION section from the current line_idx onwards
    for i in range(line_idx - 1, len(lines)):
        if lines[i].strip() == "MOTION":
            motion_start_idx = i
            break
    if motion_start_idx == -1:
        raise ValueError("MOTION section not found.")

    frame_values = []
    data_line_found = False
    
    # Iterate from after the "MOTION" keyword to find "Frames: 1" and the data line
    for i in range(motion_start_idx + 1, len(lines)):
        line = lines[i].strip()
        if line.startswith("Frames: 1"):
            # The actual motion data should be 2 lines after "Frames: 1"
            # (skip "Frame Time: X.XXX" line)
            if i + 2 < len(lines):
                motion_data_line = lines[i+2].strip()
                try:
                    frame_values = [float(x) for x in motion_data_line.split()]
                    data_line_found = True
                    break
                except ValueError:
                    raise ValueError("Could not parse motion data values (expected numbers).")
            else:
                raise ValueError("Incomplete MOTION section: Missing frame data line after 'Frame Time:'.")
    
    if not data_line_found:
        raise ValueError("Single frame motion data ('Frames: 1') not found in the MOTION section.")
    
    if len(frame_values) != len(ordered_channels_for_motion):
        print(f"Warning: Number of motion data values ({len(frame_values)}) does not match "
              f"expected channels from hierarchy ({len(ordered_channels_for_motion)}). "
              f"This might lead to incorrect animation.")

    return root_bvh_joint, all_bvh_joints, ordered_channels_for_motion, frame_values

def import_bvh_single_frame(motion_string, name, scale=100):
    """
    Imports a single-frame BVH file content into the active Cinema 4D document.
    It creates the joint hierarchy and applies the root position and joint rotations.

    Args:
        bvh_content_string (str): A string containing the full content of the .bvh file.

    Returns:
        bool: True if the import was successful, False otherwise.
    """
    doc = c4d.documents.GetActiveDocument()
    if not doc:
        print("Error: No active Cinema 4D document. Please open or create a document.")
        return False
    
    bvh_content_string = HEADER + motion_string

    try:
        lines = bvh_content_string.splitlines()
        root_bvh_joint, all_bvh_joints, ordered_channels_for_motion, frame_values = parse_bvh_data(lines, scale=scale)
    except ValueError as e:
        print(f"BVH Import Error: {e}")
        return False

    # Create a parent Null object to group all imported joints for easier management
    bvh_group_null = c4d.BaseObject(c4d.Onull)
    bvh_group_null.SetName(name)
    doc.InsertObject(bvh_group_null)

    # First pass: Create all c4d.BaseObjects (Joints, including End Sites)
    # This prepares the c4d_object references in the BVHJointData objects.
    for joint_name, bvh_joint_data in all_bvh_joints.items():
        # Both regular joints and End Sites are created as c4d.Ojoint objects
        c4d_obj = c4d.BaseObject(c4d.Ojoint)
        c4d_obj.SetName(joint_name)
        bvh_joint_data.c4d_object = c4d_obj

    # Second pass: Link the hierarchy in Cinema 4D and set relative positions (offsets)
    def build_c4d_hierarchy_recursive(bvh_joint_data, parent_c4d_obj):
        """Recursively builds the Cinema 4D object hierarchy."""
        c4d_obj = bvh_joint_data.c4d_object
        if c4d_obj:
            if parent_c4d_obj:
                c4d_obj.InsertUnder(parent_c4d_obj)
            else: # This is the root joint, insert it under the main group null
                c4d_obj.InsertUnder(bvh_group_null)
            
            # BVH joint offsets are relative to their parent's pivot.
            # In C4D, SetRelPos directly sets the object's position relative to its parent.
            c4d_obj.SetRelPos(bvh_joint_data.offset)

        # Recursively build children
        for child_bvh_joint_data in bvh_joint_data.children:
            build_c4d_hierarchy_recursive(child_bvh_joint_data, c4d_obj)

    # Start building the C4D hierarchy from the BVH root
    if root_bvh_joint and root_bvh_joint.c4d_object:
        build_c4d_hierarchy_recursive(root_bvh_joint, None) # None indicates no C4D parent initially (will be parented to bvh_group_null)

    # --- Apply motion data (root position + joint rotations) ---
    # Store parsed motion data per joint temporarily, then apply.
    joint_motion_data = {}
    for joint_name in all_bvh_joints.keys():
        joint_motion_data[joint_name] = {
            'pos': c4d.Vector(0), # Only relevant for root, otherwise remains (0,0,0)
            'rot_x': 0.0, 'rot_y': 0.0, 'rot_z': 0.0 # Stored in degrees
        }
    
    current_value_idx = 0
    # Iterate through the channels in the exact order they appear in the motion data line
    for joint_name, channel_type in ordered_channels_for_motion:
        if current_value_idx >= len(frame_values):
            print(f"Warning: Not enough motion data values to process all channels. "
                  f"Missing data for {joint_name} {channel_type}.")
            break
        
        value = frame_values[current_value_idx]
        
        # Store the value based on channel type
        if channel_type == "Xposition": joint_motion_data[joint_name]['pos'].x = value * scale
        elif channel_type == "Yposition": joint_motion_data[joint_name]['pos'].y = value * scale
        elif channel_type == "Zposition": joint_motion_data[joint_name]['pos'].z = -value * scale # Inverted z-value
        elif channel_type == "Xrotation": joint_motion_data[joint_name]['rot_x'] = value
        elif channel_type == "Yrotation": joint_motion_data[joint_name]['rot_y'] = value
        elif channel_type == "Zrotation": joint_motion_data[joint_name]['rot_z'] = value
        
        current_value_idx += 1

    # Now, iterate through all joints and apply their collected motion data
    for joint_name, data in joint_motion_data.items():
        bvh_joint_data = all_bvh_joints[joint_name]
        c4d_obj = bvh_joint_data.c4d_object
        
        if not c4d_obj:
            continue # Skip if no C4D object

        # BVH rotation order is now assumed to be ZYX intrinsic (Rotate Z, then Y, then X on local axes).
        # C4D's HPB (Heading, Pitch, Bank) corresponds to YXZ intrinsic.
        
        # Create individual rotation matrices for Z, Y, X in degrees
        mat_z = c4d.utils.MatrixRotZ(-c4d.utils.DegToRad(data['rot_z']))
        mat_y = c4d.utils.MatrixRotY(c4d.utils.DegToRad(data['rot_y']))
        mat_x = c4d.utils.MatrixRotX(c4d.utils.DegToRad(data['rot_x']))
        
        # Combine them in ZYX intrinsic order (R_Z * R_Y * R_X)
        bvh_rotation_matrix = mat_z * mat_y * mat_x
        
        if joint_name == root_bvh_joint.name:
            # Root joint: Apply absolute position and convert combined rotation to C4D HPB
            c4d_obj.SetAbsPos(data['pos'])
            root_hpb = c4d.utils.MatrixToHPB(bvh_rotation_matrix)
            c4d_obj.SetAbsRot(root_hpb) # Apply absolute rotation
        
        else: # Child joints: Apply relative rotations only
            # Convert combined rotation to C4D HPB for relative application
            joint_hpb = c4d.utils.MatrixToHPB(bvh_rotation_matrix)
            c4d_obj.SetRelRot(joint_hpb) # Apply relative rotation

    # Update the Cinema 4D scene to show the changes
    c4d.EventAdd()

    return bvh_group_null

def get_armature_data(root_c4d_object, scale=100):
    """
    Extracts the rotation and position data from a Cinema 4D armature
    in the BVH single-frame motion data format, ordered according to BVH_JOINT_ORDER.

    Args:
        root_c4d_object (c4d.BaseObject): The root Cinema 4D object (joint)
                                          of the armature.
        scale (float): The scale factor used during import. Defaults to 100.

    Returns:
        list[float]: A list of floating-point values representing the
                     joint rotations and root position in the BVH format.
                     Returns an empty list if the root_c4d_object is invalid.
    """
    if not isinstance(root_c4d_object, c4d.BaseObject):
        print("Error: Invalid root Cinema 4D object provided.")
        return []

    # Temporary dictionary to store extracted data, keyed by joint name
    # Format: {joint_name: {'pos': [x,y,z], 'rot': [z,x,y]}}
    all_joint_data = {}
    root_pos = None
    
    def traverse_hierarchy_and_extract(c4d_obj, is_root=False):
        """
        Recursively traverses the C4D armature, extracts data, and stores it.
        """
        nonlocal all_joint_data
        nonlocal root_pos

        if not c4d_obj:
            return

        joint_name = c4d_obj.GetName()
        if 'Site' not in joint_name:
            
            # 1. Get the C4D object's rotation (HPB)
            # These are in radians (Heading, Pitch, Bank = Y, X, Z intrinsic Euler)
            current_c4d_hpb_rad = c4d_obj.GetAbsRot() if is_root else c4d_obj.GetRelRot()

            # 2. Convert this C4D HPB back to a rotation matrix using C4D's YXZ order
            reconstructed_bvh_rot_matrix = c4d.utils.HPBToMatrix(current_c4d_hpb_rad, c4d.ROTATIONORDER_HPB)

            # 3. Decompose this 'reconstructed_bvh_rot_matrix' into raw ZYX intrinsic Euler angles.
            # These are the same decomposition formulas that are now correctly extracting magnitudes.
            
            # Y-rotation (Pitch - theta)
            raw_theta_y_rad = math.asin(-reconstructed_bvh_rot_matrix.v1.z)

            # X-rotation (Roll - phi)
            raw_phi_x_rad = math.atan2(reconstructed_bvh_rot_matrix.v2.z, reconstructed_bvh_rot_matrix.v3.z)
            
            # Z-rotation (Yaw - psi)
            raw_psi_z_rad = math.atan2(reconstructed_bvh_rot_matrix.v1.y, reconstructed_bvh_rot_matrix.v1.x)

            # Handle gimbal lock (theta_y_rad close to +/-90 degrees) - simplified
            # This part ensures stability if pitch is close to vertical.
            # No change needed here, as the previous iteration correctly resolved value issues.
            cos_raw_theta_y = math.cos(raw_theta_y_rad)
            if abs(cos_raw_theta_y) < 1e-6:
                raw_phi_x_rad = math.atan2(reconstructed_bvh_rot_matrix.v2.y, reconstructed_bvh_rot_matrix.v1.y)
                raw_psi_z_rad = 0.0
            
            # 4. Apply the observed corrections: swap X and Y, and negate all three.
            # These lines are crucial for getting the correct BVH X, Y, Z degrees.
            rot_x_deg = c4d.utils.RadToDeg(-raw_theta_y_rad) # BVH X should be - (raw Y from decomposition)
            rot_y_deg = c4d.utils.RadToDeg(-raw_phi_x_rad)    # BVH Y should be - (raw X from decomposition)
            rot_z_deg = c4d.utils.RadToDeg(raw_psi_z_rad)    # BVH Z should be - (raw Z from decomposition)

            # Store the extracted data in the all_joint_data dictionary
            current_joint_data = {}
            if is_root:
                # Root joint: Get absolute position
                abs_mg = c4d_obj.GetMg()
                pos = abs_mg.off / scale # Get current absolute position
                root_pos = [pos.x, pos.y, -pos.z] # Z was inverted for import, re-invert for export
                
            current_joint_data['rot'] = [rot_z_deg, rot_x_deg, rot_y_deg] # BVH rotation order: Z, X, Y
            all_joint_data[joint_name] = current_joint_data

        # Recursively call for children
        child = c4d_obj.GetDown()
        while child:
            traverse_hierarchy_and_extract(child)
            child = child.GetNext()

    # Start the traversal from the root object
    traverse_hierarchy_and_extract(root_c4d_object, is_root=True)

    # 5. Assemble the final BVH motion line in the correct order
    total_rotations = []
    for joint_name in BVH_JOINT_ORDER:
        data = all_joint_data.get(joint_name)
        if data:
            total_rotations.append(data['rot'])
            #final_bvh_motion_line.extend(data['rot'])
        else:
            print(f"Warning: Data for joint '{joint_name}' not found. Skipping or assuming zero channels.")

    return total_rotations, root_pos

def iter_hierarchy(op):
    while op:
        yield op
        if op.GetDown():
            for c in iter_hierarchy(op.GetDown()):
                yield c
        op = op.GetNext()

def safe_clone(root):
    """
    Clone *root* and return the clone.
    Warns if children were not copied (rare older versions).
    """
    clone = root.GetClone(c4d.COPYFLAGS_0)   # default keeps children
    if clone.GetDown() is None and root.GetDown():
        # Children missing → your version needs a manual recursion
        c4d.gui.MessageDialog(
            "Warning: GetClone() did not copy children.\n"
            "Please use a current build of Cinema4d."
        )
    return clone

def duplicate_chain(root, suffix):
    clone = safe_clone(root)
    name_map = {}
    for j in iter_hierarchy(clone):
        if j.CheckType(c4d.Ojoint):
            new_name = f"{j.GetName()}{suffix}"
            name_map[j.GetName()] = j
            j.SetName(new_name)
    return clone, name_map

def insert_under_null(doc, obj, name):
    """Wrap *obj* in a new Null named *name* and insert into *doc*."""
    grp = c4d.BaseObject(c4d.Onull)
    grp.SetName(name)
    doc.InsertObject(grp)
    obj.InsertUnder(grp)
    return grp

def create_fkik_skeletons(main_group):
    """
    Takes the original BVH skeleton (bind_root) and makes:
      * bind_root      (left untouched, will become BIND chain)
      * bind_root_IK   (full duplicate, renamed …_IK)
      * bind_root_FK   (full duplicate, renamed …_FK)
    Also builds three top groups:
      * <root>_Bind_Skel_Grp
      * <root>_IK_Skel_Grp
      * <root>_FK_Skel_Grp
    All under a single <root>_FullBodyRig_Grp for easy collapse.
    """
    bind_root = main_group.GetDown()
    doc = bind_root.GetDocument()
    if doc is None:
        raise RuntimeError("Object is not in a document")

    # ---------- undo safety ----------
    doc.StartUndo()

    try:
        # 1. duplicate + rename
        ik_root, ik_map = duplicate_chain(bind_root, "_IK")
        fk_root, fk_map = duplicate_chain(bind_root, "_FK")

        # 2. insert new chains into the scene
        ik_grp = insert_under_null(doc, ik_root,
                                   f"{bind_root.GetName()}_IK_Skel_Grp")
        fk_grp = insert_under_null(doc, fk_root,
                                   f"{bind_root.GetName()}_FK_Skel_Grp")

        # 3. put everything under a master rig group
        rig_grp = c4d.BaseObject(c4d.Onull)
        rig_grp.SetName(f"{bind_root.GetName()}_FullBodyRig_Grp")
        doc.InsertObject(rig_grp)

        ik_grp.InsertUnder(rig_grp)
        fk_grp.InsertUnder(rig_grp)
        bind_root.InsertUnder(rig_grp)
        rig_grp.InsertUnder(main_group) # original BVH becomes Bind chain

        # 4. freeze transforms (recommended after the −90° X import fix)
        for chain_root in (bind_root, ik_root, fk_root):
            try:
                c4d.utils.FreezeCoordinates(chain_root)   # R20+
            except AttributeError:
                pass

        # 5. mark for redraw & undo
        doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, rig_grp)
        doc.EndUndo()
        c4d.EventAdd()
        print(ik_map)
        print(fk_map)

        return {
            "bind_root": bind_root,
            "ik_root": ik_root,
            "fk_root": fk_root,
            "ik_map":  ik_map,
            "fk_map":  fk_map,
            "groups":  {"rig": rig_grp, "ik": ik_grp, "fk": fk_grp}
        }

    except Exception as e:
        # on any failure roll the scene back
        doc.EndUndo()
        doc.DoUndo(True)
        raise e

def axis_from_name(name: str) -> str:
    """Return the plane-normal axis (+X/+Y/+Z) the control should face."""
    name = name.lower()
    if any(k in name for k in ("spine", "neck", "head", "hip", "knee")):
        return "z"          # circle lies in the XY-plane   (normal +Z)
    if any(k in name for k in ("foot", "toe")):
        return "y"          # circle lies in the XZ-plane   (normal +Y)
    return "x"              # default: lie in the YZ-plane  (normal +X)

def create_fk_controls(doc: c4d.documents.BaseDocument,
                       fk_root: c4d.BaseObject,
                       radius: float = 5.0
                       ) -> tuple[c4d.BaseObject|None, dict[str, c4d.BaseObject]]:
    """
    Builds one circle control per FK joint and adds a rotation–only PSR
    constraint from the joint to that circle.
    
    Returns (top_offset_null, ctrl_map).  ctrl_map maps the **base joint
    name** (no “_FK” suffix) to the controller-Null, so other passes can
    look controllers up easily.
    """
    ctrl_data: dict[c4d.BaseObject, dict[str, c4d.BaseObject]] = {}
    ctrl_map : dict[str,          c4d.BaseObject]             = {}
    top_offset: c4d.BaseObject|None = None

    for j in fk_root.GetChildren():
        todo = [j]
        while todo:
            j = todo.pop()
            todo.extend(reversed(j.GetChildren()))

            if not j.CheckType(c4d.Ojoint):
                continue
            if j is fk_root or "site" in j.GetName().lower():
                continue

            axis = axis_from_name(j.GetName())
            ctrl = c4d.BaseObject(c4d.Onull)
            ctrl.SetName(j.GetName().replace("_FK", "_FKCtrl"))
            ctrl[c4d.NULLOBJECT_DISPLAY] = c4d.NULLOBJECT_DISPLAY_SPHERE
            ctrl[c4d.NULLOBJECT_RADIUS]  = radius

            if axis == "x":
                ctrl.SetRelRot(c4d.Vector(0, utils.DegToRad(90), 0))
            elif axis == "y":
                ctrl.SetRelRot(c4d.Vector(utils.DegToRad(90), 0, 0))

            ctrl[c4d.ID_BASEOBJECT_USECOLOR] = 2
            ctrl[c4d.ID_BASEOBJECT_COLOR]    = c4d.Vector(.3, .3, 1)

            offset = c4d.BaseObject(c4d.Onull)
            offset.SetName(f"{ctrl.GetName()}_offset")
            offset.SetMg(j.GetMg()) # global align
            ctrl.InsertUnder(offset)
            doc.InsertObject(offset)

            ctrl_data[j] = {"ctrl": ctrl, "offset": offset}
            base_name = j.GetName().removesuffix("_FK")
            ctrl_map[base_name] = ctrl
            if top_offset is None:
                top_offset = offset

            ctag = c4d.BaseTag(c4d.Tcaconstraint)
            j.InsertTag(ctag)

            ctag[c4d.ID_CA_CONSTRAINT_TAG_PSR]   = True
            ctag[c4d.ID_CA_CONSTRAINT_TAG_PSR_P] = False
            ctag[c4d.ID_CA_CONSTRAINT_TAG_PSR_S] = False
            ctag[c4d.ID_CA_CONSTRAINT_TAG_PSR_R] = True

            for ax in ("X", "Y", "Z"):
                ctag[getattr(c4d, f"ID_CA_CONSTRAINT_TAG_PSR_CONSTRAIN_R_{ax}")] = True

            ctag[c4d.ID_CA_CONSTRAINT_TAG_PSR_MAINTAIN] = True
            ctag[10001] = ctrl
            ctag[c4d.ID_CA_CONSTRAINT_TAG_PSR_WEIGHT] = 1.0

    # parenting pass (unchanged) …
    for joint, data in ctrl_data.items():
        parent_joint = joint.GetUp()
        off = data["offset"]
        world_mg = off.GetMg()
        if parent_joint in ctrl_data:
            off.InsertUnder(ctrl_data[parent_joint]["ctrl"])
        else:
            off.InsertUnder(fk_root.GetUp())
        off.SetMg(world_mg)

    c4d.EventAdd()
    return top_offset, ctrl_map

def _add_fk_driver_to_ik_joint(joint: c4d.BaseObject,
                               fk_ctrl: c4d.BaseObject) -> c4d.BaseTag:
    """Adds a rotation-only PSR constraint that follows *fk_ctrl*."""
    tag = c4d.BaseTag(c4d.Tcaconstraint)
    joint.InsertTag(tag)

    tag[c4d.ID_CA_CONSTRAINT_TAG_PSR]   = True
    tag[c4d.ID_CA_CONSTRAINT_TAG_PSR_P] = False
    tag[c4d.ID_CA_CONSTRAINT_TAG_PSR_S] = False
    tag[c4d.ID_CA_CONSTRAINT_TAG_PSR_R] = True

    for ax in ("X", "Y", "Z"):
        tag[getattr(c4d, f"ID_CA_CONSTRAINT_TAG_PSR_CONSTRAIN_R_{ax}")] = True

    tag[c4d.ID_CA_CONSTRAINT_TAG_PSR_MAINTAIN] = True
    tag[10001] = fk_ctrl
    tag[c4d.ID_CA_CONSTRAINT_TAG_PSR_WEIGHT] = 1.0
    return tag

def drive_passive_ik_joints_with_fk(doc: c4d.documents.BaseDocument,
                                    ik_map: dict[str, c4d.BaseObject],
                                    fk_ctrl_map: dict[str, c4d.BaseObject],
                                    limb_defs: list[tuple[str, str, str, str, bool]]
                                    ) -> None:
    """
    Adds a rotation-only PSR constraint to every IK joint that is *not*
    part of an IK limb chain so it follows its FK controller.
    """
    chain_bases: set[str] = set()
    for s, m, e, *_ in limb_defs:
        chain_bases.update((s, m, e))

    doc.StartUndo()
    try:
        for base_name, ik_joint in ik_map.items():
            if base_name in chain_bases:
                continue
            fk_ctrl = fk_ctrl_map.get(base_name)
            if not fk_ctrl:
                continue
            if 'Toe' in base_name:
                continue
            tag = _add_fk_driver_to_ik_joint(ik_joint, fk_ctrl)
            doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, tag)
    finally:
        doc.EndUndo()
        c4d.EventAdd()

def pole_vector_position(start, mid, end):
    A, B, C      = start.GetMg().off, mid.GetMg().off, end.GetMg().off
    A = c4d.Vector(A[0],A[2],-A[1])
    B = c4d.Vector(B[0],B[2],-B[1])
    C = c4d.Vector(C[0],C[2],-C[1])
    
    ac_norm      = (C - A).GetNormalized()
    proj_len     = (B - A).Dot(ac_norm)
    proj         = A + proj_len * ac_norm
    pole_vec     = (B - proj).GetNormalized()
    pole_vec_pos = B + (pole_vec * 20.)
    pole_vec_pos = pole_vec_pos if (pole_vec_pos - B).GetLength() < (B + pole_vec_pos).GetLength() else pole_vec_pos * -1
    
    return pole_vec_pos

def create_ik_for_limb(doc, root_j, mid_j, tip_j,
                       label, ctrl_radius=18.0):

    goal = c4d.BaseObject(c4d.Onull)
    goal.SetName(f"{label}_Goal")
    goal[c4d.NULLOBJECT_DISPLAY] = c4d.NULLOBJECT_DISPLAY_CUBE
    goal[c4d.NULLOBJECT_RADIUS]  = ctrl_radius * 1.
    goal[c4d.ID_BASEOBJECT_USECOLOR] = 2           # use custom
    goal[c4d.ID_BASEOBJECT_COLOR]    = c4d.Vector(1, 0, 0)
    tip_mg = tip_j.GetMg()
    goal.SetAbsPos(c4d.Vector(tip_mg.off[0],tip_mg.off[2],-tip_mg.off[1]))
    doc.InsertObject(goal)

    pole = c4d.BaseObject(c4d.Onull)
    pole.SetName(f"{label}_Pole")
    pole[c4d.NULLOBJECT_DISPLAY] = c4d.NULLOBJECT_DISPLAY_POINT
    pole[c4d.NULLOBJECT_RADIUS]  = ctrl_radius * .8
    pole[c4d.ID_BASEOBJECT_USECOLOR] = 2           # use custom
    pole[c4d.ID_BASEOBJECT_COLOR]    = c4d.Vector(1, 0, 0)
    pole.SetAbsPos(pole_vector_position(root_j, mid_j, tip_j))
    doc.InsertObject(pole)

    ik_tag = c4d.BaseTag(c4d.Tcaik)
    root_j.InsertTag(ik_tag)

    ik_tag[c4d.ID_CA_IK_TAG_TIP]    = tip_j
    ik_tag[c4d.ID_CA_IK_TAG_TARGET] = goal
    ik_tag[c4d.ID_CA_IK_TAG_POLE]   = pole
    ik_tag[c4d.ID_CA_IK_TAG_SOLVER] = c4d.ID_CA_IK_TAG_SOLVER_2D

    return goal, pole, ik_tag

def build_ik_systems(doc, ik_root, ik_map, fk_ctrl_map,
                     radius=8.0, grp_name_suffix="_IK_Controls_Grp"):

    limbs = [("AnymLeftArm",   "AnymLeftForearm", "AnymLeftHand",  "AnymLeftArm",  True),
         ("AnymRightArm",  "AnymRightForearm","AnymRightHand", "AnymRightArm", True),
         ("AnymLeftHip", "AnymLeftKnee",     "AnymLeftFoot",  "AnymLeftLeg",  False),
         ("AnymRightHip","AnymRightKnee",    "AnymRightFoot", "AnymRightLeg", False)]
    ctrls, tags = [], []
    for start, mid, end, label, skip in limbs:
        s, m, e = ik_map.get(start), ik_map.get(mid), ik_map.get(end)
        if not (s and m and e):
            continue
        g, p, t = create_ik_for_limb(doc, s, m, e, label,
                                     ctrl_radius=radius)
        ctrls.extend((g, p)); tags.append(t)

    if ctrls:
        grp = c4d.BaseObject(c4d.Onull)
        grp.SetName(f"{grp_name_suffix}")
        grp[c4d.NULLOBJECT_DISPLAY] = c4d.NULLOBJECT_DISPLAY_NONE
        doc.InsertObject(grp)
        for n in ctrls:
            n.InsertUnder(grp)

    drive_passive_ik_joints_with_fk(doc, ik_map, fk_ctrl_map, limbs)

    if not ctrls:
        return None

    c4d.EventAdd()
    return grp

def setup_fkik_switch_constraints(rig_data):
    """
    Sets up FK/IK switch using Cinema 4D's native constraint system.
    This is more reliable than Python tags for real-time updates.
    
    Args:
        rig_data: Dictionary from create_fkik_skeletons
    
    Returns:
        Dictionary with control_null and constraints
    """
    doc = c4d.documents.GetActiveDocument()
    if not doc:
        raise RuntimeError("No active document")
    
    doc.StartUndo()
    
    try:
        # 1. Create the control null
        control_null = c4d.BaseObject(c4d.Onull)
        control_null.SetName("CTRL_FK_IK_Switch")
        control_null[c4d.NULLOBJECT_DISPLAY] = 2  # Display as sphere
        control_null[c4d.NULLOBJECT_RADIUS] = 50
        control_null[c4d.ID_BASEOBJECT_USECOLOR] = 2  # Display color: On
        control_null[c4d.ID_BASEOBJECT_COLOR] = c4d.Vector(1, 1, 0)  # Yellow
        
        # 2. Add User Data for FK/IK switch
        bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_REAL)
        bc[c4d.DESC_NAME] = "FK/IK Mix"
        bc[c4d.DESC_MIN] = 0.0
        bc[c4d.DESC_MAX] = 100.0
        bc[c4d.DESC_CUSTOMGUI] = c4d.CUSTOMGUI_REALSLIDER
        bc[c4d.DESC_UNIT] = c4d.DESC_UNIT_PERCENT
        bc[c4d.DESC_STEP] = 1.0
        bc[c4d.DESC_DEFAULT] = 0.0
        
        mix_element = control_null.AddUserData(bc)
        control_null[mix_element] = 0.0  # Default to FK
        
        # Insert control null
        control_null.InsertUnder(rig_data["groups"]["rig"])
        doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, control_null)
        
        # 3. Set up constraints on each bind joint
        constraints = []
        
        def setup_joint_constraints(bind_joint):
            """Set up dual constraints (FK and IK) for each joint"""
            
            if 'Site' in bind_joint.GetName():
                return
            
            # Get corresponding FK and IK joints
            fk_joint = rig_data["fk_map"].get(bind_joint.GetName())
            ik_joint = rig_data["ik_map"].get(bind_joint.GetName())
            
            if not fk_joint or not ik_joint:
                return
            
            # Create FK constraint
            fk_constraint = bind_joint.MakeTag(c4d.Tconstraint)
            set_priority(fk_constraint)
            if fk_constraint:
                fk_constraint.SetName(f"FK_Constraint_{bind_joint.GetName()}")
                doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, fk_constraint)
                
                # Set to PSR constraint
                fk_constraint[c4d.ID_CA_CONSTRAINT_TAG_PSR] = True
                fk_constraint[10001] = fk_joint  # Target object
                
                # Create Xpresso to control FK weight (100% - mix)
                fk_xpresso = fk_constraint.MakeTag(c4d.Texpresso)
                fk_xpresso.SetName("FK_Weight")
                doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, fk_xpresso)
                
                master = fk_xpresso.GetNodeMaster()
                root = master.GetRoot()
                
                # Control node
                ctrl_node = master.CreateNode(root, c4d.ID_OPERATOR_OBJECT)
                ctrl_node[c4d.GV_OBJECT_OBJECT_ID] = control_null
                ctrl_port = ctrl_node.AddPort(c4d.GV_PORT_OUTPUT, mix_element)
                
                # Math node (100 - value)
                math_node = master.CreateNode(root, c4d.ID_OPERATOR_MATH)
                math_node[c4d.GV_MATH_FUNCTION_ID] = c4d.GV_MATH_SUB  # Subtract
                math_node.GetInPort(0).SetFloat(100.0)  # 100 - mix
                
                # Constraint node
                const_node = master.CreateNode(root, c4d.ID_OPERATOR_OBJECT)
                const_node[c4d.GV_OBJECT_OBJECT_ID] = fk_constraint
                weight_port = const_node.AddPort(c4d.GV_PORT_INPUT,
                    c4d.DescID(c4d.DescLevel(c4d.ID_CA_CONSTRAINT_TAG_PSR_CONS, 0, 0),
                               c4d.DescLevel(10006, 0, 0)))  # Weight parameter
                
                # Connect: control -> math input2
                master.CreateConnection(ctrl_node, ctrl_port,
                                        math_node, math_node.GetInPort(1))
                # Connect: math output -> constraint weight
                master.CreateConnection(math_node, math_node.GetOutPort(0),
                                        const_node, weight_port)
                
                constraints.append(fk_constraint)
            
            # Create IK constraint
            ik_constraint = bind_joint.MakeTag(c4d.Tconstraint)
            set_priority(ik_constraint)
            if ik_constraint:
                ik_constraint.SetName(f"IK_Constraint_{bind_joint.GetName()}")
                doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, ik_constraint)
                
                # Set to PSR constraint
                ik_constraint[c4d.ID_CA_CONSTRAINT_TAG_PSR] = True
                ik_constraint[10001] = ik_joint  # Target object
                
                # Create Xpresso to control IK weight (= mix value)
                ik_xpresso = ik_constraint.MakeTag(c4d.Texpresso)
                ik_xpresso.SetName("IK_Weight")
                doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, ik_xpresso)
                
                master = ik_xpresso.GetNodeMaster()
                root = master.GetRoot()
                
                # Control node
                ctrl_node = master.CreateNode(root, c4d.ID_OPERATOR_OBJECT)
                ctrl_node[c4d.GV_OBJECT_OBJECT_ID] = control_null
                ctrl_port = ctrl_node.AddPort(c4d.GV_PORT_OUTPUT, mix_element)
                
                # Constraint node
                const_node = master.CreateNode(root, c4d.ID_OPERATOR_OBJECT)
                const_node[c4d.GV_OBJECT_OBJECT_ID] = ik_constraint
                weight_port = const_node.AddPort(c4d.GV_PORT_INPUT,
                    c4d.DescID(c4d.DescLevel(c4d.ID_CA_CONSTRAINT_TAG_PSR_CONS, 0, 0),
                               c4d.DescLevel(10006, 0, 0)))  # Weight parameter
                
                # Connect directly: control mix -> constraint weight
                master.CreateConnection(ctrl_node, ctrl_port,
                                        const_node, weight_port)
                
                constraints.append(ik_constraint)
            
            # Process children
            child = bind_joint.GetDown()
            while child:
                setup_joint_constraints(child)
                child = child.GetNext()
        
        # Start constraint setup from bind root
        setup_joint_constraints(rig_data["bind_root"])
        
        doc.EndUndo()
        c4d.EventAdd()
        
        return {
            "control_null": control_null,
            "constraints": constraints,
            "mix_element": mix_element
        }
        
    except Exception as e:
        doc.EndUndo()
        doc.DoUndo(True)
        raise e

def setup_fkik_switch(rig_data):
    doc = c4d.documents.GetActiveDocument()
    if not doc:
        raise RuntimeError("No active document")
    
    doc.StartUndo()
    
    try:
        # Create control null
        control_null = c4d.BaseObject(c4d.Onull)
        control_null.SetName("CTRL_FK_IK_Switch")
        control_null[c4d.NULLOBJECT_DISPLAY] = c4d.NULLOBJECT_DISPLAY_DIAMOND
        control_null[c4d.NULLOBJECT_RADIUS] = 10.
        control_null[c4d.ID_BASEOBJECT_USECOLOR] = 2
        control_null[c4d.ID_BASEOBJECT_COLOR] = c4d.Vector(1, 1, 0)
        control_null.SetAbsPos(c4d.Vector(50, 50, -70))
        
        # Add slider
        bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_REAL)
        bc[c4d.DESC_NAME] = "FK/IK"
        bc[c4d.DESC_MIN] = 0.0
        bc[c4d.DESC_MAX] = 1.0
        bc[c4d.DESC_CUSTOMGUI] = c4d.CUSTOMGUI_REALSLIDER
        bc[c4d.DESC_UNIT] = c4d.DESC_UNIT_PERCENT
        bc[c4d.DESC_STEP] = 0.01
        
        element = control_null.AddUserData(bc)
        control_null[element] = 0.0
        
        control_null.InsertUnder(rig_data["groups"]["rig"])
        doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, control_null)
        
        # Create a single master Python tag on the control
        master_tag = control_null.MakeTag(c4d.Tpython)
        set_priority(master_tag)
        master_tag.SetName("FK_IK_Master_Controller")
        doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, master_tag)
        
        # Collect all joint mappings
        joint_data = []
        
        def collect_joints(bind_joint):
            if 'Site' in bind_joint.GetName():
                return
            
            fk_joint = rig_data["fk_map"].get(bind_joint.GetName())
            ik_joint = rig_data["ik_map"].get(bind_joint.GetName())
            
            if fk_joint and ik_joint:
                joint_data.append({
                    'bind_name': bind_joint.GetName(),
                    'fk_name': fk_joint.GetName(),
                    'ik_name': ik_joint.GetName()
                })
            
            child = bind_joint.GetDown()
            while child:
                collect_joints(child)
                child = child.GetNext()
        
        collect_joints(rig_data["bind_root"])
        
        # Generate Python code
        joint_list_str = str(joint_data).replace("'", '"')
        
        python_code = f'''import c4d
from c4d import utils

def main():
    # Joint mapping data
    joints = {joint_list_str}
    
    # Get FK/IK value from this object
    ctrl = op.GetObject()
    if not ctrl:
        return
    
    # Access user data properly
    mix = ctrl[c4d.ID_USERDATA, 1]  # First user data item
    
    # Process each joint
    for joint_info in joints:
        bind = doc.SearchObject(joint_info["bind_name"])
        fk = doc.SearchObject(joint_info["fk_name"])
        ik = doc.SearchObject(joint_info["ik_name"])
        
        if not bind or not fk or not ik:
            continue
        
        # Get global matrices
        fk_mg = fk.GetMg()
        ik_mg = ik.GetMg()
        
        # Blend position
        pos = fk_mg.off * (1.0 - mix) + ik_mg.off * mix
        
        # Blend rotation
        fk_rot = utils.MatrixToHPB(fk_mg)
        ik_rot = utils.MatrixToHPB(ik_mg)
        rot = fk_rot * (1.0 - mix) + ik_rot * mix
        
        # Build matrix
        mg = utils.HPBToMatrix(rot)
        mg.off = pos
        
        # Convert to local
        parent = bind.GetUp()
        if parent:
            mg = ~parent.GetMg() * mg
        
        bind.SetMl(mg)
    
    # Force redraw
    c4d.EventAdd(c4d.EVENT_ANIMATE)
'''
        
        master_tag[c4d.TPYTHON_CODE] = python_code
        
        # Set to Frame Dependent so it runs continuously
        master_tag[c4d.EXPRESSION_ENABLE] = True
        
        doc.EndUndo()
        c4d.EventAdd()
        
        return {
            "control_null": control_null,
            "master_tag": master_tag,
            "element": element
        }
        
    except Exception as e:
        doc.EndUndo()
        doc.DoUndo(True)
        raise e

def create_master_control(rig_data):
    """
    Simplified version that just creates a basic master control without extra features.
    """
    doc = c4d.documents.GetActiveDocument()
    if not doc:
        raise RuntimeError("No active document")
    
    doc.StartUndo()
    
    try:
        rig_group = rig_data["groups"]["rig"]
        bind_root = rig_data["bind_root"]
        
        # Create control curve
        control = c4d.BaseObject(c4d.Osplinecircle)
        control.SetName("CTRL_Master")
        control[c4d.PRIM_CIRCLE_RADIUS] = 40
        control[c4d.PRIM_PLANE] = c4d.PRIM_PLANE_XZ
        control[c4d.ID_BASEOBJECT_USECOLOR] = 2
        control[c4d.ID_BASEOBJECT_COLOR] = c4d.Vector(1, 0.5, 0)
        
        # Position at ground level
        bind_pos = bind_root.GetMg().off
        control.SetAbsPos(c4d.Vector(bind_pos.x, 0, bind_pos.z))
        
        # Insert and parent
        doc.InsertObject(control)
        doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, control)
        
        rig_matrix = rig_group.GetMg()
        rig_group.Remove()
        rig_group.InsertUnder(control)
        rig_group.SetMg(rig_matrix)
        
        doc.EndUndo()
        c4d.EventAdd()

        return control
        
    except Exception as e:
        doc.EndUndo()
        doc.DoUndo(True)
        raise e

def set_priority(tag, group=c4d.CYCLE_GENERATORS, offset=0):
    prio = c4d.PriorityData()
    prio.SetPriorityValue(c4d.PRIORITYVALUE_MODE, group)
    prio.SetPriorityValue(c4d.PRIORITYVALUE_PRIORITY, offset)
    tag[c4d.EXPRESSION_PRIORITY] = prio
  
def get_keyframe_indices(doc, mainGroup):
    """
    Returns a sorted list of all frame indices at which ANY CCurve
    under mainGroup has a key, including frame 0.
    """
    fps    = doc.GetFps()
    frames = set()

    def traverse(obj):
        if not obj:
            return

        for track in obj.GetCTracks():
            curve = track.GetCurve()
            for i in range(curve.GetKeyCount()):
                key   = curve.GetKey(i)
                time  = key.GetTime()
                frame = time.GetFrame(fps)
                frames.add(frame)

        child = obj.GetDown()
        while child:
            traverse(child)
            child = child.GetNext()

    traverse(mainGroup)

    return sorted(list(frames))

def api_request(data, api_key, url):
    url = f'{url}api/predict/'
    headers = {
        'X-API-KEY': f'{api_key}',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, json=data)

    return response.status_code, response.json()


class PoseSetting:
    def __init__(self):
        self.selected_armature_name = ""
        self.is_static = False
        self.frame = 1

class AnymToolDialog(gui.GeDialog):
    def __init__(self):
        super(AnymToolDialog, self).__init__()
        self.plugin_path = os.path.dirname(__file__)
        self.icon_path = os.path.join(self.plugin_path, "res", "icons")
        self.url = 'https://app.anym.tech/'
        self.tot_frames = 40
        self.poses = []
        self.logo_bitmap_gui = None

    def load_custom_bitmap(self, filename):
        """Load a custom bitmap from the icons directory"""
        bitmap_path = os.path.join(self.icon_path, filename)
        if os.path.exists(bitmap_path):
            bitmap = bitmaps.BaseBitmap()
            result, ismovie = bitmap.InitWith(bitmap_path)
            if result == c4d.IMAGERESULT_OK:
                return bitmap
        return None
    
    def CreateLayout(self):
        """Create the dialog layout"""
        self.SetTitle("ANYM v1.0")
        
        # Main group
        if self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 1, 0):
            self.GroupBorderSpace(5, 5, 5, 5)
            
            # Logo section using BitmapButtonCustomGui
            if self.GroupBegin(1000, c4d.BFH_CENTER, 1, 0):
                # Try to load and display the company logo
                logo_bitmap = self.load_custom_bitmap('ANYM.png')
                if logo_bitmap:
                    # Create bitmap button configuration
                    bc_logo = c4d.BaseContainer()
                    bc_logo[c4d.BITMAPBUTTON_BUTTON] = False  # Not clickable, just display
                    bc_logo[c4d.BITMAPBUTTON_TOGGLE] = False
                    
                    # Add the bitmap button to display the logo
                    self.logo_bitmap_gui = self.AddCustomGui(
                        IDC_LOGO_BITMAP,
                        c4d.CUSTOMGUI_BITMAPBUTTON,
                        "",
                        c4d.BFH_CENTER,
                        100,  # width
                        60,  # height
                        bc_logo
                    )
                    
                    if self.logo_bitmap_gui:
                        # Set the image (True = create internal copy)
                        self.logo_bitmap_gui.SetImage(logo_bitmap, True)
                    else:
                        self.AddStaticText(0, c4d.BFH_CENTER, name="ANYM v1.0")
                else:
                    # Fallback to text if logo can't be loaded
                    self.AddStaticText(0, c4d.BFH_CENTER, name="ANYM v1.0")
            self.GroupEnd()
            
            # Separator
            self.AddSeparatorH(0)
            
            # Poses section
            if self.GroupBegin(2000, c4d.BFH_SCALEFIT, 1, 0, "Poses"):
                self.GroupBorder(c4d.BORDER_GROUP_IN)
                self.GroupBorderSpace(5, 5, 5, 5)
                
                # Pose selection row
                if self.GroupBegin(2001, c4d.BFH_SCALEFIT, 2, 0):
                    self.AddStaticText(0, c4d.BFH_LEFT, name="Available Pose:")
                    self.AddComboBox(IDC_POSE_DROPDOWN, c4d.BFH_SCALEFIT)
                    # Add pose options here
                    # default
                    self.AddChild(IDC_POSE_DROPDOWN, 0, "--select pose--")
                    # rest of available poses
                    self.available_pose_files = list(ANYM_POSES.keys())
                    for i, pose_file in enumerate(self.available_pose_files):
                        self.AddChild(IDC_POSE_DROPDOWN, i+1, pose_file)

                self.GroupEnd()
                
                # FK/IK checkbox
                self.AddCheckbox(IDC_FKIK_CHECKBOX, c4d.BFH_LEFT, 0, 0, "Create FK/IK")
                self.SetBool(IDC_FKIK_CHECKBOX, True)
                
                # Import Armature button
                self.AddButton(IDC_IMPORT_ARMATURE, c4d.BFH_SCALEFIT, 0, 15, "Import Armature")
                
                # Add Pose button
                self.AddButton(IDC_ADD_POSE, c4d.BFH_SCALEFIT, 0, 15, "Add Pose")
                
                if self.ScrollGroupBegin(IDC_POSES_SCROLL,
                             c4d.BFH_SCALEFIT|c4d.BFV_SCALEFIT,
                             c4d.SCROLLGROUP_VERT,
                             initw=0, inith=150):
                    # this group has 6 columns: remove-btn, combo, static-cb, (maybe) frame label + frame field,
                    # plus one spacer column so it wraps neatly if too wide
                    self.GroupBegin(IDC_POSES_CONTAINER,
                        c4d.BFH_SCALEFIT|c4d.BFV_SCALEFIT,
                        1, 0)
                    self.GroupEnd()      # end IDC_POSES_CONTAINER
                    self.GroupEnd() # end ScrollGroup
                
            self.GroupEnd()
            
            # Separator
            self.AddSeparatorH(0)
            
            # Context section
            if self.GroupBegin(3000, c4d.BFH_SCALEFIT, 1, 0, "Context"):
                self.GroupBorder(c4d.BORDER_GROUP_IN)
                self.GroupBorder(c4d.BORDER_GROUP_IN)
                self.GroupBorderSpace(5, 5, 5, 5)
                
                # Total Frames
                if self.GroupBegin(3001, c4d.BFH_SCALEFIT, 2, 0):
                    self.AddStaticText(0, c4d.BFH_LEFT, name="Total Frames:")
                    self.AddEditNumberArrows(IDC_TOTAL_FRAMES, c4d.BFH_RIGHT, 80)
                    self.SetInt32(IDC_TOTAL_FRAMES, self.tot_frames)
                self.GroupEnd()
                
                # FPS
                if self.GroupBegin(3002, c4d.BFH_SCALEFIT, 2, 0):
                    self.AddStaticText(0, c4d.BFH_LEFT, name="FPS:               ")
                    self.AddEditNumberArrows(IDC_FPS, c4d.BFH_RIGHT, 80)
                    self.SetInt32(IDC_FPS, 30)
                self.GroupEnd()
                
                # Checkboxes row
                if self.GroupBegin(3003, c4d.BFH_SCALEFIT, 2, 0):
                    self.AddCheckbox(IDC_IS_LOOPING, c4d.BFH_LEFT, 0, 0, "Is Looping")
                    self.AddCheckbox(IDC_SOLVE_IK, c4d.BFH_LEFT, 0, 0, "Apply IK Solver")
                    self.SetBool(IDC_SOLVE_IK, True)
                self.GroupEnd()
                
            self.GroupEnd()
            
            # Separator
            self.AddSeparatorH(0)
            
            # Generate Animation button (main action)
            self.AddButton(IDC_GENERATE_ANIMATION, c4d.BFH_SCALEFIT, 0, 20, "Generate Animation")
            
            # Separator
            self.AddSeparatorH(0)
            
            # Fetch Animation button
            self.AddButton(IDC_FETCH_ANIMATION, c4d.BFH_SCALEFIT, 0, 15, "Fetch Exported Animation")
            
            # API Key field
            if self.GroupBegin(4000, c4d.BFH_SCALEFIT, 2, 0):
                self.AddStaticText(0, c4d.BFH_LEFT, name="API Key:")
                self.AddEditText(IDC_API_KEY, c4d.BFH_SCALEFIT)
                # Set stored API key if available
                stored_key = self.get_api_key()
                if stored_key:
                    self.SetString(IDC_API_KEY, stored_key)
                else:
                    self.SetString(IDC_API_KEY, '123456789')
            self.GroupEnd()
            
        self.GroupEnd()
        
        return True
    
    def Command(self, id, msg):
        """Handle button clicks and events"""
        if id == IDC_IMPORT_ARMATURE:
            self.import_armature()
            self.refresh_pose_list()
        elif id == IDC_ADD_POSE:
            self.add_pose()
            self.refresh_pose_list()
        elif IDC_POSE_REMOVE_BASE <= id < IDC_POSE_REMOVE_BASE + len(self.poses):
            idx = id - IDC_POSE_REMOVE_BASE
            self.remove_pose(idx)
            self.refresh_pose_list()
        elif IDC_POSE_STATIC_BASE <= id < IDC_POSE_STATIC_BASE + len(self.poses):
            idx = id - IDC_POSE_STATIC_BASE
            self.poses[idx].is_static = self.GetBool(id)
            self.refresh_pose_list()
        elif IDC_POSE_COMBO_BASE <= id < IDC_POSE_COMBO_BASE + len(self.poses):
            idx = id - IDC_POSE_COMBO_BASE
            selected_index = self.GetInt32(id)
            
            # Convert index to armature name for stable storage
            if selected_index == 0:
                self.poses[idx].selected_armature_name = ""  # No selection
            else:
                available_armatures = self.find_anym_armatures()
                armature_index = selected_index - 1
                if 0 <= armature_index < len(available_armatures):
                    self.poses[idx].selected_armature_name = available_armatures[armature_index].GetName()
                else:
                    self.poses[idx].selected_armature_name = ""
        elif IDC_POSE_FRAME_FIELD_BASE <= id < IDC_POSE_FRAME_FIELD_BASE + len(self.poses):
            idx = id - IDC_POSE_FRAME_FIELD_BASE
            self.poses[idx].frame = self.GetInt32(id)
        elif id == IDC_GENERATE_ANIMATION:
            self.generate_animation()
        elif id == IDC_FETCH_ANIMATION:
            self.exported_anim_listener()
        elif id == IDC_API_KEY:
            self.on_api_key_change()
        elif id == IDC_LOGO_BITMAP:
            # Handle logo click if needed (currently disabled)
            pass
        
        return True
    
    def get_api_key(self):
        plugin_prefs_dir = os.path.join(c4d.storage.GeGetC4DPath(1), 'Anym')
        filepath = os.path.join(plugin_prefs_dir, 'settings.json')
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                api_key = json.load(f).get('api_key', '123456789')
            return api_key.strip()
        else:
            return None
    
    def import_armature(self):
        """Import armature functionality"""
        doc = documents.GetActiveDocument()
        orig_objects = set()
        orig_object_names = list()
        obj = doc.GetFirstObject()
        while obj:
            orig_objects.add(obj)
            orig_object_names.append(obj.GetName())
            obj = obj.GetNext()

        selected_pose = self.GetInt32(IDC_POSE_DROPDOWN) - 1 # Correction for default option
        if selected_pose != -1: # default
            fkik_enabled = self.GetBool(IDC_FKIK_CHECKBOX)
            bvh_name = self.available_pose_files[selected_pose]

            pose_line = ANYM_POSES[bvh_name]
            
            base_name = bvh_name
            name = base_name
            i = 1
            while name in orig_object_names:
                name = base_name + "{:03d}".format(i)
                i += 1

            new_root = import_bvh_single_frame(pose_line, name=name)

            mg = new_root.GetMg()
            mg *= utils.MatrixRotX(utils.DegToRad(-90))
            new_root.SetMg(mg)
            
            if fkik_enabled:
                out = create_fkik_skeletons(new_root)
                fk_offset_root, fk_ctrl_map = create_fk_controls(
                    doc=doc,
                    fk_root=out["fk_root"]
                )
                ik_ctrl_grp = build_ik_systems(
                    doc=doc,
                    ik_root=out["ik_root"],
                    ik_map=out["ik_map"],
                    fk_ctrl_map=fk_ctrl_map
                )
                ik_ctrl_grp.InsertUnder(out["groups"]["ik"])
                setup_fkik_switch(out)
                master_control = create_master_control(out)
                master_control.InsertUnder(new_root)
                
                mg = master_control.GetMg()
                mg *= utils.MatrixRotX(utils.DegToRad(90))
                master_control.SetMg(mg)


            c4d.EventAdd()
            return True
        return False
    
    def add_pose(self):
        """Add pose functionality"""
        self.poses.append(PoseSetting())
    
    def remove_pose(self, idx):
        """Remove the pose at index idx."""
        if 0 <= idx < len(self.poses):
            del self.poses[idx]

    def find_anym_armatures(self):
        """
        Return a list of every “ANYM” armature root in the scene—
        i.e. the top-level joint that holds both your CTRL_Master
        and CTRL_FK_IK_Switch controls.
        """
        doc = documents.GetActiveDocument()
        found_roots = []
        visited = set()

        def recurse(op):
            while op:
                if op.GetName() == "CTRL_FK_IK_Switch":
                    root = op
                    while root.GetUp():
                        root = root.GetUp()

                    if root.GetGUID() not in visited:
                        visited.add(root.GetGUID())
                        found_roots.append(root)

                recurse(op.GetDown())
                op = op.GetNext()

        recurse(doc.GetFirstObject())
        return found_roots
    
    def refresh_pose_list(self):
        """Rebuild all rows in the dynamic container."""
        # 1) Clear out the old rows
        self.LayoutFlushGroup(IDC_POSES_CONTAINER)

        available_armatures = self.find_anym_armatures()
        available_names = [obj.GetName() for obj in available_armatures]

        # 2) Re‐add every row
        for i, pose in enumerate(self.poses):
            # compute each control's unique ID
            rem_id        = IDC_POSE_REMOVE_BASE     + i
            combo_id      = IDC_POSE_COMBO_BASE      + i
            static_lbl_id = IDC_POSE_STATIC_LABEL_BASE+ i
            static_id     = IDC_POSE_STATIC_BASE     + i
            frame_lbl_id  = IDC_POSE_FRAME_LABEL_BASE+ i
            frame_fld_id  = IDC_POSE_FRAME_FIELD_BASE+ i

            self.GroupBegin(0, c4d.BFH_SCALEFIT|c4d.BFV_CENTER, 7, 0)

            # column 1: remove button
            self.AddButton(rem_id, c4d.BFH_LEFT, name="✕")
            
            # column 2: pose dropdown
            self.AddComboBox(combo_id, c4d.BFH_SCALEFIT)
            self.AddChild(combo_id, 0, "--select pose--")
            
            # Find the correct index for the stored armature name
            selected_index = 0  # Default to "--select pose--"
            for j, name in enumerate(available_names):
                self.AddChild(combo_id, j+1, name)
                if name == pose.selected_armature_name:
                    selected_index = j + 1
            
            self.SetInt32(combo_id, selected_index)
            
            # column 3: static checkbox
            self.AddStaticText(static_lbl_id, c4d.BFH_LEFT, name="Is Static:")
            self.AddCheckbox(static_id, c4d.BFH_LEFT, 0, 0, "")
            self.SetBool(static_id, pose.is_static)
            
            # column 4: "Frame:" label
            self.AddStaticText(frame_lbl_id, c4d.BFH_LEFT, name="Frame:")
            self.HideElement(frame_lbl_id, not pose.is_static)
            
            # column 5: frame number
            self.AddEditNumberArrows(frame_fld_id, c4d.BFH_LEFT, 60)
            self.SetInt32(frame_fld_id, pose.frame)
            self.HideElement(frame_fld_id, not pose.is_static)

            self.GroupEnd()

        # 3) Tell C4D we've changed that container's layout
        self.LayoutChanged(IDC_POSES_CONTAINER)

    def format_request_data(self, doc, total_frames, fps, is_looping, solve_ik):
        fps_scene = doc.GetFps()
        original_time = doc.GetTime()

        indices_total = list()
        rots_total = list()
        root_pos_total = list()

        # Loop over poses
        for pose in self.poses:
            armature = doc.SearchObject(pose.selected_armature_name)
            main_root = armature.GetDown().GetDown().GetDown().GetNext()

            if pose.is_static:
                idx = pose.frame
                if idx > total_frames:
                    total_frames = idx
                    self.SetInt32(IDC_TOTAL_FRAMES, idx)
                rots, root_pos = get_armature_data(main_root)
                
                indices_total.append(idx)
                rots_total.append(rots)
                root_pos_total.append(root_pos)

            else:
                keyframe_indices = get_keyframe_indices(doc, armature)
                indices_total.extend(keyframe_indices)
                
                if len(keyframe_indices) == 0:
                    c4d.gui.MessageDialog(f"Warning: Pose {armature.GetName()} is set as Non-Static, but does not have any keyframes set. Please set at least one keyframe and try again.", type=c4d.GEMB_ICONEXCLAMATION)
                    return
                
                # Loop over keyframe indices
                for idx in keyframe_indices:
                    if idx / fps >= 10.:
                        c4d.gui.MessageDialog(f"Warning: The highest currently set keyframe index on armature {armature.GetName()} is {idx}, which at {fps} FPS implies an animation length of {round(idx / fps, 2)} seconds. The maximum animation duration is 10 seconds.", type=c4d.GEMB_ICONEXCLAMATION)
                        return
                    elif idx > total_frames:
                        total_frames = idx
                        self.SetInt32(IDC_TOTAL_FRAMES, idx)
                    
                    time = c4d.BaseTime(idx, fps_scene)
                    doc.SetTime(time)

                    doc.ExecutePasses(None, True, True, True, c4d.BUILDFLAGS_NONE)
                    c4d.EventAdd()

                    rots, root_pos = get_armature_data(main_root)
                    
                    rots_total.append(rots)
                    root_pos_total.append(root_pos)

        doc.SetTime(original_time)
        doc.ExecutePasses(None, True, True, True, c4d.BUILDFLAGS_NONE)
        c4d.EventAdd()

        if len(indices_total) != len(set(indices_total)):
            c4d.gui.MessageDialog(f"Warning: Two or more armatures have keyframes set on the same frame index.", type=c4d.GEMB_ICONEXCLAMATION)
            return

        zipped_sorted = sorted(
            list(zip(indices_total, rots_total, root_pos_total)),
            key=lambda t: t[0]
        )
        indices_total, rots_total, root_pos_total = map(list, zip(*zipped_sorted))
        
        data = {
            "is_looping": is_looping,
            "solve_ik": solve_ik,
            "n_frames": total_frames,
            "fps": fps,
            "indices": indices_total,
            "target_rot": rots_total,
            "target_root_pos": root_pos_total,
        }

        return data

    def generate_animation(self):
        """Generate animation"""
        
        if len(self.poses) == 0:
            c4d.gui.MessageDialog("Warning: No poses are selected. Add a pose by clicking 'Add Pose'.", type=c4d.GEMB_ICONEXCLAMATION)
            return
        
        if any([pose.selected_armature_name == "" for pose in self.poses]):
            c4d.gui.MessageDialog("Warning: Not all poses in the Anym Plugin have a pose selected. Please select a compatible armature for each pose in the Poses section.", type=c4d.GEMB_ICONEXCLAMATION)
            return

        doc = c4d.documents.GetActiveDocument()
        total_frames = self.GetInt32(IDC_TOTAL_FRAMES)
        fps = self.GetInt32(IDC_FPS)
        is_looping = self.GetBool(IDC_IS_LOOPING)
        solve_ik = self.GetBool(IDC_SOLVE_IK)
        api_key = self.GetString(IDC_API_KEY)

        if len(api_key) == 0:
            c4d.gui.MessageDialog("Warning: Please enter your Anym API Key.", type=c4d.GEMB_ICONEXCLAMATION)
            return

        data = self.format_request_data(doc, total_frames, fps, is_looping, solve_ik)

        status_code, output = api_request(data, api_key, self.url)

        if status_code == 200:
            anim_id = output['data']['animation_id']

            webbrowser.open(
                f'{self.url}preview/{anim_id}/', new=0
            )

        else:
            try:
                c4d.gui.MessageDialog(f"Error {status_code}: {output['error']}", type=c4d.GEMB_ICONEXCLAMATION)
            except:
                c4d.gui.MessageDialog(f"Error {status_code}: {output['message']}", type=c4d.GEMB_ICONEXCLAMATION)
            return
    
    def exported_anim_listener(self):
        """Fetch exported animation functionality"""
        try:
            api_key = self.GetString(IDC_API_KEY)
            
            headers = {
                'X-API-KEY': f'{api_key}',
                'Content-Type': 'application/json'
            }

            response = requests.get(f'{self.url}api/import-animation/', headers=headers)
            
            if response.status_code == 200:
                doc = documents.GetActiveDocument()

                orig_objects = set()
                orig_object_names = list()
                obj = doc.GetFirstObject()
                while obj:
                    orig_objects.add(obj)
                    orig_object_names.append(obj.GetName())
                    obj = obj.GetNext()
                
                plugin_prefs_dir = os.path.join(c4d.storage.GeGetC4DPath(1), 'Anym')
                os.makedirs(plugin_prefs_dir, exist_ok=True)
                filepath = os.path.join(plugin_prefs_dir, 'AnymOutput.bvh')
                with open(filepath, 'w') as f:
                    f.write(response.json()['data'])
                
                
                FLAGS = (c4d.SCENEFILTER_MERGESCENE
                        | c4d.SCENEFILTER_OBJECTS
                        | c4d.SCENEFILTER_MATERIALS)
                        
                if not documents.MergeDocument(doc, filepath, FLAGS):
                    raise RuntimeError(f"Failed to import pose: {filepath}")
                
                obj = doc.GetFirstObject()
                while obj:
                    if obj not in orig_objects:
                        new_root = obj
                        break

                new_root.SetAbsScale(c4d.Vector(100.))
                
                base_name = 'AnymOutput'
                name = base_name + ""
                i = 1
                while name in orig_object_names:
                    name = base_name + "{:03d}".format(i)
                    i += 1

                new_root.SetName(name)
                mg = new_root.GetMg()
                mg *= utils.MatrixRotX(utils.DegToRad(-90))
                new_root.SetMg(mg)
            else:
                c4d.gui.MessageDialog(f"Error {response.status_code}: {response.json()['message']}", type=c4d.GEMB_ICONEXCLAMATION)
        except:
            c4d.gui.MessageDialog(f"Error importing Anym animation.", type=c4d.GEMB_ICONEXCLAMATION)
    
    def on_api_key_change(self):
        """Handle API key changes"""
        key = self.GetString(IDC_API_KEY)
        plugin_prefs_dir = os.path.join(c4d.storage.GeGetC4DPath(1), 'Anym')
        os.makedirs(plugin_prefs_dir, exist_ok=True)
        filepath = os.path.join(plugin_prefs_dir, 'settings.json')
        with open(filepath, 'w') as json_file:
            json.dump({'api_key': key}, json_file)
        

class AnymToolCommand(c4d.plugins.CommandData):
    def Execute(self, doc):
        dialog = AnymToolDialog()
        return dialog.Open(dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=PLUGIN_ID,
                          defaultw=340, defaulth=680)
    
    def GetState(self, doc):
        return c4d.CMD_ENABLED

def main():
    return c4d.plugins.RegisterCommandPlugin(
        id=PLUGIN_ID,
        str="Anym",
        info=0,
        dat=AnymToolCommand(),
        help="Anym Animation Tool"
    )

if __name__ == "__main__":
    dialog = AnymToolDialog()
    dialog.Open(dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=PLUGIN_ID, defaultw=340, defaulth=680)
