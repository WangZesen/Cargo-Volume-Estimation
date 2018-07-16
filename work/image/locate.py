import cv2, copy
import numpy as np

def findFeaturePoint(ir_image, device_tag):

    gray = cv2.cvtColor(ir_image, cv2.COLOR_BGR2GRAY)
    gray = np.float32(gray)

    dst = cv2.cornerHarris(gray, 9, 7, k = 0.04)
    dst = cv2.dilate(dst, None)

    if device_tag == 'device1':
        corner = dst > 0.01 * dst.max()
        for i in xrange(ir_image.shape[0] - 1, -1, -1):
            for j in range(ir_image.shape[1]):
                if corner[i][j]:
                    return (i - 5, j + 5)
    else:
        corner = dst > 0.01 * dst.max()
        for i in range(ir_image.shape[1]):
            for j in range(ir_image.shape[0]):
                if corner[j][i]:
                    return (j + 2, i + 3)
    return (-1, -1)


def drawFeaturePoint(ir_image, pos):
    ir_mark = copy.copy(ir_image)
    if pos[0] != -1:
        for i in range(3):
            for j in range(3):
                try:
                    ir_mark[pos[0] + i - 1][pos[1] + j - 1] = [0, 0, 255]
                except:
                    pass
    return ir_mark

def fitMoveDirection(points):
    np_points = np.array(points)
    line = cv2.fitLine(np_points, cv2.DIST_L2, 0, 0, 0.01)
    length = np.sqrt(line[0][0] ** 2 + line[1][0] ** 2 + line[2][0] ** 2)
    return [line[0][0] / length, line[1][0] / length, line[2][0] / length]

def calOffset(point_x, point_y, direction):
    k = (point_x[0] - point_y[0]) / direction[0]
    return [k * direction[0], k * direction[1], k * direction[2]]

if __name__ == '__main__':

    for i in range(76):
        image_path = '../../raw_data/cache2/1_ir_{}.jpg'.format(str(i).zfill(4))
        img = cv2.imread(image_path)
        if type(img) == type(None):
            break
        pos = findFeaturePoint(img, 'device1')
        print (pos)

        blur_img = cv2.medianBlur(img, 5)

        if pos[0] != -1:
            for i in range(3):
                for j in range(3):
                    try:
                        blur_img[pos[0] + i - 1][pos[1] + j - 1] = [0, 0, 255]
                    except:
                        pass
            pos = (pos[0] + 13, pos[1] - 5)
            for i in range(3):
                for j in range(3):
                    try:
                        blur_img[pos[0] + i - 1][pos[1] + j - 1] = [0, 0, 255]
                    except:
                        pass


        cv2.imshow('test', blur_img)
        key = cv2.waitKey(0)
        if key == ord('q'):
            break
