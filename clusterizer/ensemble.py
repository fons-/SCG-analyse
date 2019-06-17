from clusterizer.cluster import Cluster
import logging
class ClusterEnsemble:
    """
    A Rectangle Ensemble should be a set of Cluster objects
    The whole set makes the ensemble
    Each set in the ensemble represents a rectangle of arbitrary shape
    The Rectangle objects in each Cluster are 'rectangels' which combine to make a rectangle
    """

    def __init__(self, clusters):
        """
        :param clusters: The Cluster objects to be added to this ClusterEnsemble
        :type clusters: collection of class:`clusterizer.ensemble.Cluster`
        """
        self.clusters = set(clusters)

    @staticmethod
    def from_iterable(rectangle_iterable):
        """
        Creates a ClusterEnsemble from an iterable containing Rectangle objects.
        Each Rectangle will be added to its own Cluster, creating a layered structure.
        This structure signifies that each Rectangle in the iterable is disjunct from all others.

        :param rectangle_iterable: The clusters to create a ClusterEnsemble with
        :type rectangle_iterable: iterable of class:`clusterizer.rectangle.Rectangle`

        :return: A ClusterEnsemble containing Clusters with all Clusters from the iterable
        :rtype: class:`clusterizer.ensemble.ClusterEnsemble`
        """
        ensemble = set()
        for x in rectangle_iterable:
            ensemble.add(Cluster([x]))
        return ClusterEnsemble(ensemble)

    def __str__(self):
        return "{" + ("\n".join(str(c) for c in sorted(self.clusters))) + "}"

    def __repr__(self):
        return str(self)

    def __hash__(self):
        """
        A hash function that computes a number based on the Clusters in the underlying Clusters
        Use case: Adding ClusterEnsembles to dictionaries, sets, etc.
        This function is cryptographically weak and should not be used for security purposes.

        :return: A hash of the ClusterEnsemble
        :rtype: int
        """
        hashed = 0
        for c in self.clusters:
            hashed += hash(c)
        return hashed

    def __iter__(self):
        """
        Creates an iterator over the ClusterEnsemble. Mirrors behaviour of sets.
        This makes expressions like `for c in my_clusterensemble` possible,
        so you don't have to type `for c in my_clusterensemble.as_set()`

        :return: An iterator over the Clusters in this ClusterEnsemble
        :rtype: iterator
        """
        return self.clusters.__iter__()

    def __bool__(self):
        """
        Boolean representation of a ClusterEnsemble. Mirrors behaviour of sets.

        :return: False if self.clusters is empty, True if non-empty
        :rtype: bool
        """
        return bool(self.clusters)

    def __len__(self):
        """
        Number of Clusters in the ClusterEnsemble. Mirrors behaviour of sets.

        :return: The length of self.clusters
        :rtype: int
        """
        return len(self.clusters)

    def get_rectangles(self):
        """
        Creates a single set containing all the Rectangles from each Cluster in this ClusterEnsemble.

        :return: All Rectangles from all Clusters in this ClusterEnsemble
        :rtype: set of class:`clusterizer.rectangle.Rectangle`
        """
        result = set()
        for s in self.clusters:
            for rect in s:
                result.add(rect)
        return result

    def flatten(self):
        """Returns a Cluster containing all Rectangles contained in _any_ Cluster of this ClusterEnsemble.

        :return: A Cluster of all Rectangles in all Clusters in this ClusterEnsemble
        :rtype: class:`clusterizer.ensemble.Cluster
        """
        logging.warn("DEPRECATED: Use `Cluster(ensemble.get_rectangles())` instead.")
        result = set()
        for c in self:
            result |= set(c)
        return Cluster(result)

    def get_clusters(self):
        """
        Returns the Clusters in this ClusterEnsemble, without casting to a specific collection type.

        :return: The Clusters in this ClusterEnsemble
        :rtype: Collection of class:`clusterizer.ensemble.Cluster`
        """
        logging.warn("DEPRECATED: Use `ensemble.clusters` instead.")
        return self.clusters

    def as_set(self):
        """
        Returns a set containing the Clusters in this ClusterEnsemble.

        :return: The Clusters in this ClusterEnsemble
        :rtype: set of class:`clusterizer.ensemble.Cluster`
        """
        logging.warn("DEPRECATED: Use `set(ensemble)` instead.")
        return set(self.clusters)

    def as_list(self):
        """
        Returns a list containing the Clusters in this ClusterEnsemble.

        :return: The Clusters in this ClusterEnsemble
        :rtype: list of class:`clusterizer.ensemble.Cluster`
        """
        logging.warn("DEPRECATED: Use `list(ensemble)` instead.")
        return list(self.clusters)

    def disjunct(self, other):
        """
        Determines if two ClusterEnsembles are disjunct. That is, disjunct(self, other) returns:
        - True if self and other do not contain any overlap in any of their Clusters
        - False if self and other overlap in any of their Clusters
        So: self & other has to be empty for disjunct(self, other) to be True.

        :param other: The other ClusterEnsemble to compare self to
        :type other: class:`clusterizer.ensemble.ClusterEnsemble`

        :return: False if self and other have overlap, True otherwise.
        :rtype: bool
        """
        return not bool(self & other)

    def __and__(self, other):
        """
        Calculates the overlap between two ClusterEnsembles, overloading the & operator.
        This is done by calculating the overlap between the underlying Cluster objects.
        In doing so, it keeps track of which algorithms found the Clusters in the Clusters.

        :param other: The other ClusterEnsemble to calculate the overlap with
        :type other: class:`clusterizer.ensemble.ClusterEnsemble`

        :return: The overlap between self and other
        :rtype: class:`clusterizer.ensemble.ClusterEnsemble`
        """
        result = set()
        for cs1 in self:
            for cs2 in other:
                overlap = cs1 & cs2
                if overlap:
                    result.add(overlap)
        return ClusterEnsemble(result)

    def __or__(self, other):
        """
        Calculates the bounding box of two ClusterEnsembles, overloading the | operator.h
        This is done by calculating the bounding box of the underlying Cluster objects.
        For overlapping Rectangle objects in the Clusters, the bounding box is calculated.
        Separate Clusters are kept separate. If there are Cluster objects that are disjunct from all others,
        the resulting ClusterEnsemble will contain multiple Cluster objects.

        :param other: The other ClusterEnsemble to calculate the bounding box with
        :type other: class:`clusterizer.ensemble.ClusterEnsemble`

        :return: The bounding boxes of the clusters in the Clusters in self and other
        :rtype: class:`clusterizer.ensemble.ClusterEnsemble`
        """
        if self.disjunct(other):
            return ClusterEnsemble(self.clusters | other.clusters)
        result = ClusterEnsemble(self.clusters)
        helper = ClusterEnsemble(other.clusters)
        while helper:
            helpercur = helper.clusters.pop()
            for rcur in result:
                if not helpercur.disjunct(rcur):
                    helper.clusters.add(helpercur | rcur)
                    result.clusters.remove(rcur)
                    break
            else:
                result.clusters.add(helpercur)
        return result

    def __add__(self, other):
        """
        Calculates the rich set-theoretic union of two ClusterEnsembles, overloading the + operator.
        This is done by calling the + operator on the underlying Cluster objects.
        In doing so, it keeps track of which algorithms found the clusters.
        The best analogy for the result is a Venn diagram. The overlapping parts are where the algorithms agree. Unlike &, + also remembers where the algorithms disagree.

        :param other: The other ClusterEnsemble to calculate the union with
        :type other: class:`clusterizer.ensemble.ClusterEnsemble`

        :return: The set-theoretic union of the Clusters in self and other
        :rtype: class:`clusterizer.ensemble.ClusterEnsemble`
        """
        if self.disjunct(other):
            return ClusterEnsemble(self.clusters | other.clusters)
        result = ClusterEnsemble(self.clusters)
        helper = ClusterEnsemble(other.clusters)
        while helper:
            helpercur = helper.clusters.pop()
            for rcur in result:
                if not helpercur.disjunct(rcur):
                    helper.clusters.add(helpercur + rcur)
                    result.clusters.remove(rcur)
                    break
            else:
                result.clusters.add(helpercur)
        return result

    def most_confident(self):
        """
        Returns a ClusterEnsemble with for each Cluster in `self` the Clusters in that Cluster with the highest number of algorithms that found it.
        Confidence doesn't have to be the same for each Cluster. For example, one Cluster could contain overlap while another is only found by one algorithm. In this case, for the first Cluster, only the overlap is returned, while for the second Cluster, it is returned in its entirety.

        :return: The Clusters in each Cluster with the highest number of algorithms that found it
        :rtype: ClusterEnsemble
        """
        result = set()
        for c in self:
            result.add(c.most_confident())
        return ClusterEnsemble(result)
