'''
Grid-based Approximation
'''

class GridApproximation(object):
    '''Grid-based Approximation'''    
    def __init__(self, distance_fun, update_value_fun, threshold):
        '''distance_fun return the distance between two point in grid
            update_value_fun is helping funtion help to update/combine old value and new value
            threshold the distance between two point in the grid.
        '''
        self._distance_fun = distance_fun
        self._update_value_fun = update_value_fun
        self.threshold = threshold
        self._grid = {}
        
    def __iter__(self):
        for p, v in self._grid.iteritems():
            yield p, v
            
    def __str__(self):
        items = []
        for p, v in self:
            items.append('%s\t%s' % (p, v))
        return '\n'.join(items)

    def __setitem__(self, point, value):
        '''call add method'''
        self.add(point, value)

    def __getitem__(self, point):
        '''get the value of the approximated point'''
        apoint = self.get_approximated_point(point)
        if apoint is not None:
            return self._grid[apoint]
        return None

    def add(self, point, value):
        '''Add the given point if its distance to existed points is larger than threshold
            If there is existed approximated point, the value will be used to update/combine to old value
        '''
        apoint = self.get_approximated_point(point)
        if apoint is None:
            self._grid[point] = value
        else:
            self.update(apoint, value)        
    
    def update(self, point, new_value):
        #Todo: Check error, the point is not exist
        self._grid[point] = self._update_value_fun(self._grid[point], new_value)

    def get_value(self, point):
        #Todo: Check error, the point is not exist
        return self._grid[point]

    def get_nearest_point(self, point):
        npoint = None
        min_d = None
        for p, v in self:
            d = self._distance_fun(p, point)
            #print p, d
            if min_d is None or min_d > d:
                min_d = d
                npoint = p
        return npoint

    def get_approximated_point(self, point):
        npoint = self.get_nearest_point(point)
        if npoint is not None and self._distance_fun(npoint, point)<self.threshold:
            return npoint
        return None
    
    def existed_approximated_point(self, point):
        apoint = self.get_approximated_point(point)
        return apoint is not None

    def get_total_point_number(self):
        return len(self._grid.keys())

    def is_empty(self):
        return self.get_total_point_number()==0

##    def _standard_point(self, point):
##        if isinstance(point, list):
##            point = tuple(point)
##        return point
            



