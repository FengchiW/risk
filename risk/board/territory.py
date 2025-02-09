###############################################################################
# Defines risk territories
#
import risk.logger


class Territory(object):
    def __init__(self, name, neighbours=None):
        self.name = name
        self.neighbours = {} if not neighbours else neighbours
        self.reset(True)

    def reset(self, reset_owner=False):
        self.armies = 0
        if reset_owner:
            self.owner = None

    def add_neighbour(self, neighbour):
        self.neighbours[neighbour.name] = neighbour
        neighbour.neighbours[self.name] = self

    def is_neighbour(self, neighbour):
        return neighbour.name in self.neighbours

    def set_troops(self, number_of_armies):
        # TODO check for valid number of armies
        self.armies = number_of_armies

    def closest_enemy_distance(self):
        # Breadth first search
        # note that each entry in the to_visit queue is (node_to_visit, path)
        # so that we can measure distance when we find closest enemy territory
        # -1 represents infinite distance
        # n >= 0 means distance from this node
        NOT_FOUND = -1
        visited = set()
        to_visit = [(self, [])]
        closest = None
        while len(to_visit) > 0 and not closest:
            visiting = to_visit.pop()
            visited.add(visiting[0])
            if visiting[0].owner != self.owner:
                closest = visiting
            else:
                for neighbour in list(visiting[0].neighbours.values()):
                    if not neighbour in visited:
                        to_visit.append(
                            (neighbour, visiting[1] + [visiting[0]]))
        if not closest:
            return NOT_FOUND
        else:
            return len(closest[1])

    def is_connected(self, target):
        # naive depth first search
        # warning, this operation is VERY expensive!
        return Territory._graph_connection_search(self, target, set([self]))

    def __str__(self):
        return "[%s]\n" \
            "Owner: %s\n" \
            "Neighbours: %s\n" \
            "Armies: %s\n" % \
            (self.name, self.owner, self.neighbours, self.armies)

    def __repr__(self):
        return self.name

    @staticmethod
    def _graph_connection_search(current, target, visited):
        if current == target:
            return True
        else:
            found = False
            neighbours = [x for x in list(current.neighbours.values()) if x.owner == current.owner and
                          not x in visited]
            while len(neighbours) > 0 and not found:
                next_node = neighbours.pop()
                visited.add(next_node)
                found = Territory._graph_connection_search(
                    next_node, target, visited)
            return found


class ContinentBuilder(object):
    def __init__(self, tag):
        self.graph = {}
        self.tag = tag

    def border(self, territory0, territory1):
        self.create_territory_if_needed(territory0)
        self.create_territory_if_needed(territory1)
        self.graph[territory0].add_neighbour(self.graph[territory1])

    def borders(self, list_of_borders):
        for border in list_of_borders:
            self.border(border[0], border[1])

    def create_territory_if_needed(self, territory):
        if territory not in self.graph:
            self.graph[territory] = Territory(territory)

    def validate(self):
        if len(self.graph) == 0:
            risk.logger.warn(
                "graph with tag %s appears to be empty" % self.tag)
        else:
            disjoint = ContinentBuilder.flood_graph(self.graph)
            if len(disjoint) > 0:
                risk.logger.warn(
                    "graph with tag %s has disjoint territories: [%s]" %
                    (self.tag, ', '.join([t.name for t in disjoint]))
                )
            else:
                risk.logger.debug("tag [%s] passed!" % self.tag)

    def get_mapping(self):
        self.validate()
        return self.graph

    @staticmethod
    def flood_graph(graph):
        start = graph[list(graph.keys())[0]]
        visited = set([start])
        targets = set(list(start.neighbours.values()))
        while len(targets) > 0:
            current = targets.pop()
            if not current in visited:
                visited.add(current)
                for neighbour in list(current.neighbours.values()):
                    targets.add(neighbour)
                    targets -= visited
            if len(current.neighbours) <= 1:
                risk.logger.warn("%s looks suspicious..." % current.name)
        return set(list(graph.values())) - visited


def generate_north_america_continent():
    risk.logger.debug('Generating North America...')
    builder = ContinentBuilder('generate_north_america_continent')
    builder.borders([
        ('alaska', 'northwest_territory'),  # 0
        ('alaska', 'alberta'),  # 1
        ('northwest_territory', 'greenland'),  # 2
        ('northwest_territory', 'ontario'),  # 3
        ('northwest_territory', 'alberta'),  # 4
        ('alberta', 'ontario'),  # 5
        ('alberta', 'western_united_states'),  # 6
        ('greenland', 'eastern_canada'),  # 7
        ('greenland', 'ontario'),  # 8
        ('ontario', 'eastern_canada'),  # 9
        ('ontario', 'eastern_united_states'),  # 10
        ('ontario', 'western_united_states'),  # 11
        ('western_united_states', 'eastern_united_states'),  # 12
        ('western_united_states', 'central_america'),  # 13
        ('eastern_canada', 'eastern_united_states'),  # 14
        ('eastern_united_states', 'central_america'),  # 15
    ])
    risk.logger.debug('Generated North America!')
    return builder.get_mapping()


def generate_south_america_continent():
    risk.logger.debug('Generating South America...')
    builder = ContinentBuilder('generate_south_america_continent')
    builder.borders([
        ('venezuela', 'brazil'),
        ('venezuela', 'peru'),
        ('brazil', 'peru'),
        ('brazil', 'argentina'),
        ('peru', 'argentina'),
    ])
    risk.logger.debug('Generated South America!')
    return builder.get_mapping()


def generate_africa_continent():
    risk.logger.debug('Generating Africa...')
    builder = ContinentBuilder('generate_africa_continent')
    builder.borders([
        ('egypt', 'north_africa'),
        ('egypt', 'east_africa'),
        ('north_africa', 'east_africa'),
        ('north_africa', 'central_africa'),
        ('east_africa', 'central_africa'),
        ('east_africa', 'south_africa'),
        ('east_africa', 'madagascar'),
        ('central_africa', 'south_africa'),
        ('south_africa', 'madagascar'),
    ])
    risk.logger.debug('Generated Africa!')
    return builder.get_mapping()


def generate_australia_continent():
    risk.logger.debug('Generating Australia...')
    builder = ContinentBuilder('generate_australia_continent')
    builder.borders([
        ('indonesia', 'new_guinea'),
        ('indonesia', 'western_australia'),
        ('new_guinea', 'western_australia'),
        ('new_guinea', 'eastern_australia'),
        ('western_australia', 'eastern_australia'),
    ])
    risk.logger.debug('Generated Australia!')
    return builder.get_mapping()


def generate_europe_continent():
    risk.logger.debug('Generating Europe...')
    builder = ContinentBuilder('generate_europe_continent')
    builder.borders([
        ('iceland', 'great_britain'),
        ('iceland', 'scandinavia'),
        ('great_britain', 'northern_europe'),
        ('great_britain', 'scandinavia'),
        ('scandinavia', 'northern_europe'),
        ('scandinavia', 'russia'),
        ('northern_europe', 'western_europe'),
        ('northern_europe', 'southern_europe'),
        ('northern_europe', 'russia'),
        ('western_europe', 'southern_europe'),
        ('russia', 'southern_europe'),
    ])
    risk.logger.debug('Generated Europe!')
    return builder.get_mapping()


def generate_asia_continent():
    risk.logger.debug('Generating Asia...')
    builder = ContinentBuilder('generate_asia_continent')
    builder.borders([
        ('siberia', 'ural'),
        ('siberia', 'china'),
        ('siberia', 'mongolia'),
        ('siberia', 'irkutsk'),
        ('siberia', 'yakutsk'),
        ('ural', 'afghanistan'),
        ('ural', 'china'),
        ('china', 'afghanistan'),
        ('china', 'india'),
        ('china', 'mongolia'),
        ('china', 'southern_asia'),
        ('mongolia', 'irkutsk'),
        ('mongolia', 'kamchatka'),
        ('mongolia', 'japan'),
        ('irkutsk', 'yakutsk'),
        ('irkutsk', 'kamchatka'),
        ('yakutsk', 'kamchatka'),
        ('afghanistan', 'middle_east'),
        ('afghanistan', 'india'),
        ('kamchatka', 'japan'),
        ('middle_east', 'india'),
        ('india', 'southern_asia'),
    ])
    risk.logger.debug('Generated Asia!')
    return builder.get_mapping()
