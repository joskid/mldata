"""
Convert from and to HDF5 (spec of mldata.org)

Structure of the HDF5 Format
============================

This will be the generic storage for all kinds of data sets. The basic
abstraction is that a data set is a large collection of objects having
the same type, so to say a large array.

/mldata           integer = 0
/name             Name of the data set
/comment          Initial comment
/attribute_names  Array of Strings: names of the attributes
/attribute_types  Array of Strings: description of the attribute types (see below)
/attributes       Array of Objects as described by attribute_types

Note that the distinction what is input/output, label/target depends
on the TASK, not on the data set itself!

Attribute Types
---------------

We make a distinction between the actual binary format and the
attribute type stored in the file. For example, nominal data might be
stored as integers or even bytes for efficiency, although they are
mapped to symbolic names to the outside.

The attribute type is specified by a string which has to be parsed for
better flexibility.

Supported types are:

"NUMERIC"
Numerical values
Stored as: array of numerical type

"NOMINAL(VALUE1, VALUE2, ...)"
Enumeration type
Stored as: array of small integer types

"STRING"
Stored as: an array of strings

As we see more data types, more type descriptors will be added.


Currently supported formats
===========================
to hdf5
LibSVM
ARFF

from hdf5
ARFF
"""

import h5py, numpy, os
from scipy.sparse import csc_matrix


NAME = 'hdf5conv'
VERSION = '0.2'
VERSION_MLDATA = '0'
NUM_EXTRACT = 10
COMPRESSION = 'gzip'


def progress(msg):
    """Print the given message with some kind of progress indicator.

    @param msg: messsage to print
    @type msg: string
    """
    #print ' -> ' + msg
    pass



class Converter():
    """Base class for conversion"""

    def __init__(self, in_filename, out_filename):
        """Construct a converter.

        @param in_filename: name of in-file
        @type in_filename: string
        @param out_filename: name of out-file
        @type out_filename: string
        """
        self.in_filename = in_filename
        self.out_filename = out_filename
        self.attrs = {
            'mldata': VERSION_MLDATA,
            'name': '',
            'comment': '',
        }


    def run(self):
        """Run the actual conversion process.

        'Abstract base method' to be implemented by child classes.

        @raise Exception: if child class hasn't overriden this
        """
        raise Exception('Not implemented yet!')


    def write_hdf5(self, *args, **kwargs):
        """Write an HDF file (spec of mldata.org).

        Keyword arguments are written as datasets where they key specifies the
        name and the value the data.
        """
        progress('writing out-file ' + self.out_filename)
        h = h5py.File(self.out_filename, 'w')

        progress('writing datasets')
        for key, val in kwargs.iteritems():
            h.create_dataset(key, data=val)

        progress('writing attributes')
        for key, val in self.attrs.iteritems():
            h.attrs[key] = val

        h.close()



class LibSVM2HDF5(Converter):
    """Convert a file from LibSVM to HDF5

    This is simple enough, so it doesn't need its own module.
    """

    def _parse_line(self, line):
        need_label = True
        need_idx = False
        need_val = False
        in_val = False
        idx = []
        val = []
        label = []
        items = []
        for c in line:
            if need_label:
                if c.isspace():
                    need_label = False
                    need_idx = True
                else:
                    label.append(c)
            elif need_idx:
                if c == ':':
                    need_idx = False
                    need_val = True
                elif not c.isspace():
                    idx.append(c)
            elif need_val:
                if not c.isspace():
                    in_val = True
                    val.append(c)
                elif in_val:
                    in_val = False
                    need_val = False
                    need_idx = True
                    items.append([''.join(idx), ''.join(val)])
                    idx = []
                    val = []

        return (''.join(label), items)


    def get_matrix(self):
        """Retrieves a SciPy Compressed Sparse Column matrix from infile."""
        progress('constructing csc matrix from ' + self.in_filename)
        indices = []
        indptr = [0]
        data = []
        ptr = 0
        infile = open(self.in_filename, 'r')
        for line in infile:
            label, items = self._parse_line(line)
            try:
                data.append(numpy.double(label))
            except ValueError:
                data.append(label)
            ptr += 1
            indices.append(0)
            for item in items:
                indices.append(int(item[0]))
                data.append(numpy.double(item[1]))
                ptr += 1
            indptr.append(ptr)
        infile.close()

        return csc_matrix((numpy.array(data), numpy.array(indices), numpy.array(indptr)))


    def run(self):
        """Run the actual conversion process."""
        progress('running the conversion')
        A = self.get_matrix()
        h = h5py.File(self.out_filename, 'w')
        if A.nnz/numpy.double(A.shape[0]*A.shape[1]) < 0.5: # sparse
            h.create_dataset('attributes_indices', data=A.indices, compression=COMPRESSION)
            h.create_dataset('attributes_indptr', data=A.indptr, compression=COMPRESSION)
            h.create_dataset('attributes_data', data=A.data, compression=COMPRESSION)
            self.attrs['comment'] = 'libsvm sparse'
            dim_max = numpy.max(A.indices)
        else: # dense
            A = A.todense()
            h.create_dataset('attributes', data=A, compression=COMPRESSION)
            self.attrs['comment'] = 'libsvm dense'
            dim_max = len(A[0])

        attribute_names = ['label / target', 'dim 1', '...', 'dim ' + str(dim_max)]
        h.create_dataset('attribute_names', data=attribute_names, compression=COMPRESSION)

        self.attrs['name'] = os.path.basename(self.out_filename).split('.')[0]
        for key, val in self.attrs.iteritems():
            h.attrs[key] = str(val)
        h.close()




class ARFF2HDF5(Converter):
    """Convert a file from ARFF to HDF5 (spec of mldata.org).

    It uses the module arff provided by the dataformat project:
    http://mloss.org/software/view/163/
    """

    def run(self):
        """Run the actual conversion process."""
        import arff
        a = arff.ArffFile.load(self.in_filename)

        progress('gathering HDF5 attributes')
        self.attrs['name'] = a.relation
        self.attrs['comment'] = a.comment

        progress('gathering HDF5 datasets')
        attribute_names = a.attributes
        attributes = a.data
        attribute_types = []
        for key, val in a.attribute_types.iteritems():
            if a.attribute_data[key]:
                data = ','.join(a.attribute_data[key])
                val = val + '(' + data + ')'
            val = key + ':' + val
            attribute_types.append(val)

        self.write_hdf5(
            attribute_names=attribute_names, attribute_types=attribute_types,
            attributes=attributes)


class HDF52ARFF(Converter):
    """Convert a file from HDF5 (spec of mldata.org) to ARFF

    It uses the module arff provided by the dataformat project:
    http://mloss.org/software/view/163/
    """

    def run(self):
        """Run the actual conversion process."""
        import arff
        a = arff.ArffFile()
        h = h5py.File(self.in_filename, 'r')

        progress('retrieving from HDF5 attributes')
        a.relation = h.attrs['name']
        a.comment = h.attrs['comment']

        progress('retrieving from HDF5 datasets')
        a.data = h['attributes']
        a.attributes = h['attribute_names']
        for htype in h['attribute_types']:
            sep = htype.find(':')
            attr = htype[:sep]
            type = htype[sep+1:]
            idx = type.find('(')
            if idx != -1:
                # +1/-1 -> commas
                data = type[idx+1:-1].split(',')
                type = type[:idx]
            else:
                data = None
            a.attribute_types[attr] = type
            a.attribute_data[attr] = data

        h.close()
        a.save(self.out_filename)


def hdf5_extract(filename):
    """Get an extract from an HDF file.

    @param filename: filename to extract data from
    @type filename: string
    @return: an extract of the given HDF5 file.
    @rtype: string
    """
    h = h5py.File(filename, 'r')
    extract = {}

    attrs = ['mldata', 'name', 'comment']
    for attr in attrs:
        try:
            extract[attr] = h.attrs[attr]
        except KeyError:
            pass

    dsets = ['attribute_names', 'attribute_types']
    for dset in dsets:
        try:
            extract[dset] = h[dset][:]
        except KeyError:
            pass

    # only first NUM_EXTRACT items of attributes
    try:
        extract['attributes'] = []
        if 'attributes_indptr' in h: # sparse
            # taking all data takes to long for quick viewing, but having just
            # this extract may result in less columns displayed than indicated
            # by attributes_names
            data = h['attributes_data'][:h['attributes_indptr'][NUM_EXTRACT+1]]
            indices = h['attributes_indices'][:h['attributes_indptr'][NUM_EXTRACT+1]]
            indptr = h['attributes_indptr'][:NUM_EXTRACT+1]
            A=csc_matrix((data, indices, indptr)).todense().T
        else: # dense
            A=numpy.matrix(h['attributes']).T

        for i in xrange(NUM_EXTRACT):
            extract['attributes'].append(A[i].tolist()[0])
    except KeyError:
        pass
    except ValueError:
        pass

    h.close()
    return extract


def hdf5_split(filename, name, indices):
    """Create an HDF5 split file.

    @param filename: name of the split file
    @type filename: string
    @param name: name of the Task item
    @type name: string
    @param indices: split indices
    @type indices: dict
    """
    h = h5py.File(filename, 'w')
    for k,v in indices.iteritems():
        data = []
        for row in v:
            r = []
            for col in row:
                r.append(numpy.double(col))
            data.append(r)
        h.create_dataset(k, data=data, compression=COMPRESSION)

    h.attrs['name'] = name
    h.attrs['mldata'] = 0
    h.attrs['comment'] = 'split file'
    h.close()
