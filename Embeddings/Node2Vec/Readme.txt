The python 'ToEdgelist.py' file obtains the data from PostgreSQL and converts the road segments to a networkX edgelist.
To obtain the embeddings, you need to download SNAP from https://github.com/snap-stanford/snap

The applications in SNAP have to be compiled under linux, which is done by (use sudo if necessary):

apt install build-essential
cd *snap root directory*

modify the file glib-core/bd.cpp

below #elif defined(GLib_GLIBC) || defined(GLib_BSD) you add:

struct __exception {
    int    type;      /* Exception type */
    char*  name;      /* Name of function causing exception */
    double arg1;      /* 1st argument to function */
    double arg2;      /* 2nd argument to function */
    double retval;    /* Function return value */
};

save the file.

Then cd *snap root directory*

type: make all

After it is finished compiling, you can run the Node2Vec binary under examples/node2vec.
Review the readme under the node2vec example folder in SNAP for documentation on Node2Vec arguments.