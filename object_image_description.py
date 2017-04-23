#!/usr/bin/python


def absToRel(total, value):
    return (value / total) * 2 - 1

class ObjectImageDescription:
    def __init__(self):
        self.isPresent = True

        self.imageHeight = 0
        self.imageWidth = 0

        self.angle = 0
        self.x = 0.0
        self.y = 0.0
        self.xRel = 0.0
	self.yRel = 0.0
        self.height = 0
        self.width = 0

        self.xLeftTop = 0.0
        self.yLeftTop = 0.0
        self.xRightTop = 0.0
        self.yRightTop = 0.0

        self.xLeftBottom = 0.0
        self.yLeftBottom = 0.0
        self.xRightBottom = 0.0
        self.yRightBottom = 0.0

    def getDictionary(self, cornersRot):
        dictResult = {}

        if not self.isPresent:
            angle = 0.0
        else:
            angle = (self.angle if self.angle <= 180.0 else self.angle - 360.0) / 180.0

        dictResult["is_present"] = 1.0 if self.isPresent else 0.0
        dictResult["angle"] = angle
        dictResult["x"] = self.x if self.isPresent else 0.0
        dictResult["y"] = self.y if self.isPresent else 0.0
        dictResult["x_rel"] = (self.x / self.imageWidth) * 2 - 1 if self.isPresent else 0.0
	dictResult["y_rel"] = (self.y / self.imageHeight) * 2 - 1 if self.isPresent else 0.0
        dictResult["height"] = self.height if self.isPresent else 0
        dictResult["width"] = self.width if self.isPresent else 0

        dictResult["x_left_top"] = absToRel(self.imageWidth, self.x + cornersRot[0][0]) \
                if self.isPresent else 0.0
        dictResult["y_left_top"] = absToRel(self.imageHeight, self.y + cornersRot[0][1]) \
                if self.isPresent else 0.0

        dictResult["x_right_top"] = absToRel(self.imageWidth, self.x + cornersRot[1][0]) \
                if self.isPresent else 0.0
        dictResult["y_right_top"] = absToRel(self.imageHeight, self.y + cornersRot[1][1]) \
                if self.isPresent else 0.0

        dictResult["x_left_bottom"] = absToRel(self.imageWidth, self.x + cornersRot[2][0]) \
                if self.isPresent else 0.0
        dictResult["y_left_bottom"] = absToRel(self.imageHeight, self.y + cornersRot[2][1]) \
                if self.isPresent else 0.0

        dictResult["x_right_bottom"] = absToRel(self.imageWidth, self.x + cornersRot[3][0]) \
                if self.isPresent else 0.0
        dictResult["y_right_bottom"] = absToRel(self.imageHeight, self.y + cornersRot[3][1]) \
                if self.isPresent else 0.0

        return dictResult
