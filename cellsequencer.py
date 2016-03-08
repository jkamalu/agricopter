# This module determines the most efficient sequence in which
# to traverse the cells of a field that has already been
# decomposed into cells.

import oxpath

class SequenceElement:
    def __init__(self, polygon, start_point, end_point,
                 start_top, start_left):
        self.polygon = polygon
        self.start = start_point
        self.end = end_point
        self.start_top = start_top # if False, starts on bottom
        self.start_left = start_left # if False, starts on right
        self.distance_to_end = None
        self.next = None
    

def generate_sequence(cells, path_radius):
    """
    Accepts a list of polygonal cells in arbitrary order.
    Returns a list of SequenceElement objects representing all
    the cells originally given, sorted and with start and end
    points marked for optimal coverage of the field.
    """
    elem = sequence_helper(cells, None, path_radius)
    sequence = []
    while elem is not None:
        sequence.append(elem)
        elem = elem.next

    return sequence

def sequence_helper(cells, prev_element, path_radius):
    if len(cells) == 0:
        return None
    else:
        possibilities = []
        for i in xrange(0, len(cells)):
            options = oxpath.coverage_options(cells[i],
                                              path_radius)
            cells_copy = list(cells)
            cells_copy.pop(i)

            def distance_func(option):
                next = sequence_helper(cells_copy,
                                       option,
                                       path_radius)
                option.next = next
                
                if next is None:
                    option.distance_to_end = 0
                else:
                    option.distance_to_end = next.distance_to_end

                if prev_element is not None:
                    option.distance_to_end += (
                        prev_element.end.distance(option.start))

                return option.distance_to_end
            
            best_option = min(options, key=distance_func)
            possibilities.append(best_option)
        
        return min(possibilities, key=lambda possibility:
                   possibility.distance_to_end)
