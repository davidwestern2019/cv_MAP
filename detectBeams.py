import cv2 as cv
import utilities_cv

def detectBeams(staff, img_slice_of_staff, black_head_template_height, black_head_template_width):
    # find beams for an entire piece of music
    # INPUTS: staves - a list of StaffClass objects
    # OUTPUTS: staves - edited list of StaffClass objects

    # get some parameters
    h = black_head_template_height
    w = black_head_template_width
    dis = staff.dis         #
    middle_line = staff.l3  # row coordinate of middle staff line

    for i in range(0, len(staff.notes)-1):
        note1 = staff.notes[i]
        note2 = staff.notes[i+1]
        # check if both are "quarter" notes.
        if note1.orig_dur == 1 and note2.orig_dur == 1:
            # find coordinates for left note (note1)
            if note1.y_val < middle_line:
                # Note is below middle line. Stem points up
                topLeft_x = note1.x_val
                topLeft_y = note1.y_val - 4*dis + h/2
                botLeft_x = note1.x_val
                botLeft_y = note1.y_val - 3*dis + h/2
                leftTop = (topLeft_x, topLeft_y)
                leftBot = (botLeft_x, botLeft_y)
            else:
                # Note is above middle line. Stems points down
                topLeft_x = note1.x_val
                topLeft_y = note1.y_val + 3*dis - h/2
                botLeft_x = note1.x_val
                botLeft_y = note1.y_val + 4*dis - h/2
                leftTop = (topLeft_x, topLeft_y)
                leftBot = (botLeft_x, botLeft_y)

            # find coordinates for right note (note 2)
            if note2.y_val < middle_line:
                # Note is below middle line. Stem points up
                topRight_x = note2.x_val
                topRight_y = note2.y_val - 4*dis + h/2
                botRight_x = note2.x_val
                botRight_y = note2.y_val - 3*dis + h/2
                rightTop = (topRight_x, topRight_y)
                rightBot = (botRight_x, botRight_y)
            else:
                # Note is above middle line. Stems points down
                topLeft_x = note1.x_val
                topLeft_y = note1.y_val + 3 * dis - h / 2
                botLeft_x = note1.x_val
                botLeft_y = note1.y_val + 4 * dis - h / 2
                rightTop = (topLeft_x, topLeft_y)
                rightBot = (botLeft_x, botLeft_y)

            # Set threshold
            threshold = 0.8

            # Check if there is beam between them
            if isThereBeam(leftTop, leftBot, rightTop, rightBot, img_slice_of_staff, threshold):
                note1.duration = 1/2
                note2.duration = 1/2
                staff.notes[i] = note1
                staff.notes[i+1] = note2
                print("Note ", i, " and ", i+1, " are eighth notes")

    return staff
    # end of detectBeams

def isThereBeam(leftTop, leftBot, rightTop, rightBot, image, threshold):
    # Looks for a beam in the given search area
    # INPUTs: four tuples of the coordinates for the vertices of the parallelogram
    # -- image: music without staff lines
    # -- threshold: fraction from 0 to 1. multiplied by area of search area
    # OUTPUTs: boolean. True if there is a beam. False otherwise

    # initialize the parallelogram object
    search_area = ParallelogramClass(leftTop, rightTop, leftBot, rightBot)
    search_area.findSlope()

    # create search box
    if leftTop[1] < rightTop[1]:
        print("Going down")
        box_height = int(rightBot[1] - leftTop[1])    # height of search box
        box_width = int(rightBot[0] - leftTop[0])     # width of search box
        box_topRow = int(leftTop[1])
        box_topCol = int(leftTop[0])
        box_botRow = int(rightBot[1])
        box_botCol = int(rightBot[0])
        crop_img = image[box_topRow:box_botRow, box_topCol:box_botCol]
    else:
        # print("Going up")
        box_height = int(leftBot[1] - rightTop[1])   # box height
        # print(box_height)
        box_width = int(rightBot[0] - leftTop[0])     # width of search box
        # print(box_width)
        box_topRow = int(rightTop[1])
        box_rightCol = int(rightTop[0])
        box_botRow = int(leftBot[1])
        box_leftCol = int(leftBot[0])
        # print(box_topRow, "",box_botRow, "", box_leftCol, "", box_rightCol)
        crop_img = image[box_topRow:box_botRow, box_leftCol:box_rightCol]
        # print(crop_img.shape)

    # win_name = "Cropped Image for Beam Search"
    # cv.namedWindow(win_name, cv.WINDOW_NORMAL)
    # cv.imshow(win_name, crop_img)
    # cv.waitKey(0)

    black_count = 0
    for row in range(0,box_height):
        for col in range(0,box_width):
            # Check if point is inside parallelogram
            point = (row, col)
            if search_area.isInside(point): # if point is inside search area
                if image[row, col] == 0:   # if point is black
                    black_count += 1

    if black_count >= threshold*search_area.getArea():
        return True
    else:
        return False

class ParallelogramClass:
    m = 0
    bTop = 0
    bBot = 0

    def __init__(self,coord1,coord2,coord3,coord4):
        # first element of tuple is x coordinate (col), 2nd is y coordinate (row)
        self.topLeft = coord1
        self.topRight = coord2
        self.botLeft = coord3
        self.botRight = coord4

    def findSlope(self):
        # find slope of diagonal sides of parallelogram
        self.m = (self.topRight[1]-self.topLeft[1])/(self.topRight[0]-self.topLeft[0])
        self.bTop = self.topRight[1] - self.m*self.topRight[0]
        self.bBot = self.botRight[1] - self.m * self.botRight[0]

    def getArea(self):
        # find area (# pixels) of shape
        height = self.topLeft[1] - self.botLeft[1]
        width = self.topRight[0]-self.topLeft[0]
        return height*width

    def isInside(self, point):
        # Is a point within the parallelogram?
        x = point[0]    # x coord of query point
        y = point[1]    # y coord of query point
        is_Between_Left_and_Right = False
        is_Between_Top_and_Bottom = False
        if x >= self.topLeft[0] and x <= self.topRight[0]:
            is_Between_Left_and_Right = True

        yTop = self.m *x +self.bTop    # y coordinate of parallelogram top line at given x
        yBot = self.m * x + self.bBot  # y coordinate of parallelogram bottom line at given x
        if y <= yTop and y >= yBot:
            is_Between_Top_and_Bottom = True

        if is_Between_Top_and_Bottom and is_Between_Left_and_Right:
            return True
        else:
            return False

def main():
    # Test beam detector

    # Use this to use a piece of sample music
    file_name = "example_music_7.jpg"
    orig_img = cv.imread(file_name, cv.IMREAD_GRAYSCALE)
    _, test_img = cv.threshold(orig_img, 180, 255, cv.THRESH_BINARY)

    # create window to look at test image and click on pixels for verification purposes
    picked_point = []
    pick_window = "Test Image"
    cv.namedWindow(pick_window, cv.WINDOW_NORMAL)
    cv.setMouseCallback(pick_window, utilities_cv.get_xy, picked_point)
    cv.imshow(pick_window, test_img)
    cv.waitKey(0)

    print("Testing the beamDetector...")
    result = isThereBeam(picked_point[0], picked_point[1], picked_point[2], picked_point[3], test_img, 0.3)
    print("Is there a beam? ", result)

if __name__ == '__main__':
    main()