
def jaccard(list_a, list_b):
    """
    Calculates the jaccard index from two python lists.

    :param list_a: First list
    :param list_b: Other list
    :return: The jaccard index
    """
    union_count = len(set(list_a + list_b))
    intersection_count = len(set(list_a).intersection(set(list_b)))

    return intersection_count/union_count

