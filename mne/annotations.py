# Authors: Jaakko Leppakangas <jaeilepp@student.jyu.fi>
#
# License: BSD (3-clause)

import numpy as np
from datetime import datetime
import time
import json


class Annotations(object):
    """Annotation object for annotating segments of raw data.

    Parameters
    ----------
    onset: array of float, shape (n_annotations,)
        Annotation time onsets from the beginning of the recording.
    duration: array of float, shape (n_annotations,)
        Durations of the annotations.
    description: array of str, shape (n_annotations,)
        Array of strings containing description for each annotation.
    orig_time: float | int | instance of datetime | array of int | None
        A POSIX Timestamp, datetime or an array containing the timestamp as the
        first element and microseconds as the second element. Determines the
        starting time of annotation acquisition. If None (default),
        starting time is determined from beginning of raw data.
    """

    def __init__(self, onset, duration, description, orig_time=None):

        if orig_time is not None:
            if isinstance(orig_time, datetime):
                orig_time = float(time.mktime(orig_time.timetuple()))
            elif not np.isscalar(orig_time):
                orig_time = orig_time[0] + orig_time[1] / 1000000.
            else:  # isscalar
                orig_time = float(orig_time)  # np.int not serializable
        self.orig_time = orig_time

        onset = np.array(onset)
        if onset.ndim != 1:
            raise ValueError('Onset must be a one dimensional array.')
        duration = np.array(duration)
        if duration.ndim != 1:
            raise ValueError('Duration must be a one dimensional array.')
        if not (len(onset) == len(duration) == len(description)):
            raise ValueError('Onset, duration and description must be '
                             'equal in sizes.')
        # sort the segments by start time
        order = onset.argsort(axis=0)
        self.onset = onset[order]
        self.duration = duration[order]
        self.description = np.array(description)[order]

    def _serialize(self):
        """Function that serializes the annotation object for saving."""
        return json.dumps({'onset': self.onset.tolist(),
                           'duration': self.duration.tolist(),
                           'description': self.description.tolist(),
                           'orig_time': self.orig_time})


def _combine_annotations(annotations, last_samps, sfreq):
    """Helper for combining a tuple of annotations."""
    if not all(annotations):
        return None
    elif annotations[0] is None:
        return annotations[1]
    elif annotations[1] is None:
        return annotations[0]

    if annotations[1].orig_time is None:
        onset = (annotations[1].onset + sum(last_samps[:-1]) / sfreq)
    else:
        onset = annotations[1]
    onset = np.r_[annotations[0].onset, onset]
    duration = np.r_[annotations[0].duration, annotations[1].duration]
    description = np.r_[annotations[0].description, annotations[1].description]
    return Annotations(onset, duration, description, annotations[0].orig_time)
