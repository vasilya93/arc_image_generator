#!/usr/bin/python

class Rectangle:
    def __init__(self, top, bottom, left, right):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right

    def doesIntersectRectangles(self, rectangles):
        doesInt = False
        for rect in rectangles:
            # top left corner
            doesInt = doesInt or (self.left > rect.left and \
                self.left < rect.right and self.top > rect.top and self.top < rect.bottom)
            # bottom left corner
            doesInt = doesInt or (self.left > rect.left and \
                self.left < rect.right and self.bottom > rect.top and self.bottom < rect.bottom)
            # top right corner
            doesInt = doesInt or (self.right > rect.left and \
                self.right < rect.right and self.top > rect.top and self.top < rect.bottom)
            # bottom right corner
            doesInt = doesInt or (self.right > rect.left and \
                self.right < rect.right and self.bottom > rect.top and self.bottom < rect.bottom)

            doesInt = doesInt or (rect.left > self.left and \
                rect.left < self.right and rect.top > self.top and rect.top < self.bottom)
            doesInt = doesInt or (rect.left > self.left and \
                rect.left < self.right and rect.bottom > self.top and rect.bottom < self.bottom)
            doesInt = doesInt or (rect.right > self.left and \
                rect.right < self.right and rect.top > self.top and rect.top < self.bottom)
            doesInt = doesInt or (rect.right > self.left and 
                rect.right < self.right and rect.bottom > self.top and rect.bottom < self.bottom)

            doesInt = doesInt or (self.left < rect.left and \
                self.right > rect.right and self.top > rect.top and self.bottom < rect.bottom)
            doesInt = doesInt or (rect.left < self.left and \
                rect.right > self.right and rect.top > self.top and rect.bottom < self.bottom)

        return doesInt
