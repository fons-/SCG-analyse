from functools import total_ordering
import numpy as np
import pandas as pd
from . import cluster


class ClusterSet:
    """
    A set of Cluster objects
    In a ClusterEnsemble, this represents one cluster
    """
    def __init__(self, clusters):
        self.clusters = set(clusters)

    def __str__(self):
        result = "{"
        for cluster in self.clusters:
            result += str(cluster) + "\n"
        return result[:-1] + "}"

    def __repr__(self):
        return str(self)

    def __bool__(self):
        return bool(self.clusters)

    def __len__(self):
        return len(self.clusters)

    def __iter__(self):
        return self.clusters.__iter__()

    def get_clusters(self):
        return self.clusters

    def as_set(self):
        return set(self.clusters)

    def as_list(self):
        return list(self.clusters)

    def disjunct(self, other):
        return not bool(self & other)

    def __and__(self, other):
        result = set()
        for c1 in self:
            for c2 in other:
                overlap = c1 & c2
                if overlap is not None:
                    result.add(overlap)
        return ClusterSet(result)

    def __mul__(self, other):
        return self & other

    def __or__(self, other):
        if self.disjunct(other):
            return ClusterSet(self.clusters | other.clusters)
        result = ClusterSet(self.clusters)
        helper = ClusterSet(other.clusters)
        while helper:
            helpercur = helper.clusters.pop()
            for clust in result:
                if not helpercur.disjunct(clust):
                    helper.clusters.add(helpercur | clust)
                    result.clusters.remove(clust)
                    break
            else:
                result.clusters.add(helpercur)
        return result

    def __add__(self, other):
        if self.disjunct(other):
            return ClusterSet(self.clusters | other.clusters)
        result = ClusterSet(self.clusters)
        helper = ClusterSet(other.clusters)
        while helper:
            helpercur = helper.clusters.pop()
            for clust in result:
                if not helpercur.disjunct(clust):
                    helper.clusters |= helpercur + clust
                    result.clusters.remove(clust)
                    break
            else:
                result.clusters.add(helpercur)
        return result

    def get_partial_discharges(self, circuit):
        partial_discharges = None
        for cluster in self.clusters:
            if partial_discharges is None:
                partial_discharges = cluster.get_partial_discharges(circuit)
            else:
                partial_discharges = pd.concat([partial_discharges, cluster.get_partial_discharges(circuit)], ignore_index=True)
        return partial_discharges

    def most_confident(self):
        result = set()
        confidence = 0
        for cluster in self:
            if len(cluster.found_by) > confidence:
                result = set([cluster])
                confidence = len(cluster.found_by)
            elif len(cluster.found_by) == confidence:
                result.add(cluster)
        return ClusterSet(result)

class ClusterEnsemble:
    """
    A Cluster Ensemble should be a set of ClusterSet objects
    The whole set makes the ensemble
    Each set in the ensemble represents a cluster of arbitrary shape
    The Cluster objects in each ClusterSet are 'rectangels' which combine to make a cluster
    """
    def __init__(self, sets):
        self.sets = set(sets)

    @staticmethod
    def from_iterable(cluster_iterable):
        ensemble = set()
        for x in cluster_iterable:
            ensemble.add(ClusterSet([x]))
        return ClusterEnsemble(ensemble)
        
    def __str__(self):
        result = "{"
        for cluster in self:
            result += str(cluster) + "\n"
        return result[:-1] + "}"
    
    def __repr__(self):
        return str(self)

    def __hash__(self):
        hashed = 0
        for cluster in self.sets:
            hashed += hash(cluster)
        return hashed

    def __iter__(self):
        return self.sets.__iter__()

    def __bool__(self):
        return bool(self.sets)

    def __len__(self):
        return len(self.sets)

    def get_clusters(self):
        result = set()
        for s in self.sets:
            for clust in s:
                result.add(clust)
        return result

    def flatten(self):
        result = set()
        for clusterset in self:
            result |= clusterset.as_set()
        return ClusterEnsemble([ClusterSet(result)])
    
    def as_set(self):
        return self.sets
    
    def as_list(self):
        return list(self.sets)

    def disjunct(self, other):
        return not bool(self & other)

    def __and__(self, other):
        result = set()
        for cs1 in self:
            for cs2 in other:
                overlap = cs1 & cs2
                if overlap:
                    result.add(overlap)
        return result

    def __or__(self, other):
        if self.disjunct(other):
            return ClusterEnsemble(self.sets | other.sets)
        result = ClusterEnsemble(self.sets)
        helper = ClusterEnsemble(other.sets)
        while helper:
            helpercur = helper.sets.pop()
            for rcur in result:
                if not helpercur.disjunct(rcur):
                    helper.sets.add(helpercur | rcur)
                    result.sets.remove(rcur)
                    break
            else:
                result.sets.add(helpercur)
        return result

    def __add__(self, other):
        if self.disjunct(other):
            return ClusterEnsemble(self.sets | other.sets)
        result = ClusterEnsemble(self.sets)
        helper = ClusterEnsemble(other.sets)
        while helper:
            helpercur = helper.sets.pop()
            for rcur in result:
                if not helpercur.disjunct(rcur):
                    helper.sets.add(helpercur + rcur)
                    result.sets.remove(rcur)
                    break
            else:
                result.sets.add(helpercur)
        return result

    def most_confident(self):
        result = set()
        for clusterset in self:
            result.add(clusterset.most_confident())
        return ClusterEnsemble(result)

