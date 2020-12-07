import cv2 as cv
import utilities_cv

def detectBeams(staves):
    # find beams for an entire piece of music
    # INPUTS: staves - a list of StaffClass objects
    # OUTPUTS: staves - edited list of StaffClass objects
    pass

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
    if search_area.m <= 0:
        print("Going down")
        box_height = rightBot[1] - leftTop[1]    # height of search box
        box_width = rightBot[0] - leftTop[0]     # width of search box
        box_topRow = leftTop[1]
        box_topCol = leftTop[0]
        box_botRow = rightBot[1]
        box_botCol = rightBot[0]
        crop_img = image[box_topRow:box_botRow, box_topCol:box_botCol]
    else:
        print("Going up")
        box_height = leftBot[1] - rightTop[1]   # box height
        print(box_height)
        box_width = rightBot[0] - leftTop[0]     # width of search box
        print(box_width)
        box_topRow = rightTop[1]
        box_rightCol = rightTop[0]
        box_botRow = leftBot[1]
        box_leftCol = leftBot[0]
        crop_img = image[box_topRow:box_botRow, box_leftCol:box_rightCol]
        print(crop_img.shape)

    win_name = "Cropped Image for Beam Search"
    cv.namedWindow(win_name, cv.WINDOW_NORMAL)
    cv.imshow(win_name, crop_img)
    cv.waitKey(0)

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