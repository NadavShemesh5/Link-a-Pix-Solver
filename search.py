"""
In search.py, you will implement generic search algorithms
"""

import util


class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def get_start_state(self):
        """
        Returns the start state for the search problem
        """
        util.raiseNotDefined()

    def is_goal_state(self, state):
        """
        state: Search state

        Returns True if and only if the state is a valid goal state
        """
        util.raiseNotDefined()

    def get_successors(self, state):
        """
        state: Search state

        For a given state, this should return a list of triples,
        (successor, action, stepCost), where 'successor' is a
        successor to the current state, 'action' is the action
        required to get there, and 'stepCost' is the incremental
        cost of expanding to that successor
        """
        util.raiseNotDefined()

    def get_cost_of_actions(self, actions):
        """
        actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.  The sequence must
        be composed of legal moves
        """
        util.raiseNotDefined()


class Node:
    def __init__(self, state, parent, action, aggr_cost):
        self.state = state
        self.parent = parent
        self.action = action
        self.aggr_cost = aggr_cost


def search(fringe, problem, heuristic=None, start_state=None):
    is_priority = not(type(fringe) is util.Queue or type(fringe) is util.Stack)
    start_node = Node(state=(problem.get_start_state() if start_state is None else start_state), parent=None, action=None, aggr_cost=0)
    fringe.push(start_node, 0) if is_priority else fringe.push(start_node)
    closed = set()
    while not fringe.isEmpty():
        current = fringe.pop()
        if problem.is_goal_state(current.state):
            return get_actions(node=current)
        elif current.state not in closed:
            successors = problem.get_successors(current.state)
            for suc in successors:
                suc_node = Node(state=suc[0], parent=current, action=suc[1],
                                aggr_cost=current.aggr_cost + suc[2])

                fringe.push(suc_node, suc_node.aggr_cost + (heuristic(suc[0], problem) if heuristic is not None else 0)) if is_priority else fringe.push(suc_node)
            closed.add(current.state)


def get_actions(node):
    actions = []
    temp = node
    while temp.parent:
        actions.insert(0, temp.action)
        temp = temp.parent
    return actions


def depth_first_search(problem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches
    the goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

	print("Start:", problem.get_start_state().state)
    print("Is the start a goal?", problem.is_goal_state(problem.get_start_state()))
    print("Start's successors:", problem.get_successors(problem.get_start_state()))
    """
    "*** YOUR CODE HERE ***"
    return search(util.Stack(), problem)



def breadth_first_search(problem):
    """
    Search the shallowest nodes in the search tree first.
    """
    return search(util.Queue(), problem)


def uniform_cost_search(problem):
    """
    Search the node of least total cost first.
    """
    "*** YOUR CODE HERE ***"
    return search(util.PriorityQueue(), problem)



def null_heuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0


def a_star_search(problem, heuristic=null_heuristic):
    """
    Search the node that has the lowest combined cost and heuristic first.
    """
    "*** YOUR CODE HERE ***"
    return search(util.PriorityQueue(), problem, heuristic)


# Abbreviations
bfs = breadth_first_search
dfs = depth_first_search
astar = a_star_search
ucs = uniform_cost_search
