#!/usr/bin/python

class Rectangle:
    def __init__(self, top, bottom, left, right):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right

    # Checks every rectangle in the list 'rectangles' to understand whether it overlaps
    # with the current 'self' rectangle.
    def doesOverlapRectangles(self, rectangles):
        doesOverlap = False
        for rect in rectangles:
            # top left corner
            doesOverlap = doesOverlap or (self.left > rect.left and \
                self.left < rect.right and self.top > rect.top and self.top < rect.bottom)
            # bottom left corner
            doesOverlap = doesOverlap or (self.left > rect.left and \
                self.left < rect.right and self.bottom > rect.top and self.bottom < rect.bottom)
            # top right corner
            doesOverlap = doesOverlap or (self.right > rect.left and \
                self.right < rect.right and self.top > rect.top and self.top < rect.bottom)
            # bottom right corner
            doesOverlap = doesOverlap or (self.right > rect.left and \
                self.right < rect.right and self.bottom > rect.top and self.bottom < rect.bottom)

            doesOverlap = doesOverlap or (rect.left > self.left and \
                rect.left < self.right and rect.top > self.top and rect.top < self.bottom)
            doesOverlap = doesOverlap or (rect.left > self.left and \
                rect.left < self.right and rect.bottom > self.top and rect.bottom < self.bottom)
            doesOverlap = doesOverlap or (rect.right > self.left and \
                rect.right < self.right and rect.top > self.top and rect.top < self.bottom)
            doesOverlap = doesOverlap or (rect.right > self.left and 
                rect.right < self.right and rect.bottom > self.top and rect.bottom < self.bottom)

            if doesOverlap:
                break

        return doesOverlap

    # Checks every rectangle in the list 'rectangles' to understand whether it intersects
    # with the current 'self' rectangle.
    def doesIntersectRectangles(self, rectangles):
        doesIntersect = False
        for rect in rectangles:
            doesIntersect = doesIntersect or (self.left < rect.left and \
                self.right > rect.right and self.top > rect.top and self.bottom < rect.bottom)
            doesIntersect = doesIntersect or (rect.left < self.left and \
                rect.right > self.right and rect.top > self.top and rect.bottom < self.bottom)

            if doesIntersect:
                break

        return doesIntersect
