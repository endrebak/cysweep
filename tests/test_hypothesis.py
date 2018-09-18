import pandas as pd

from chromsweep.src.chromsweep import SortedList

import pytest
from hypothesis import given, settings, reproduce_failure, unlimited, HealthCheck, seed
from hypothesis.extra.pandas import data_frames, columns, range_indexes, column
from hypothesis.extra.numpy import arrays
import hypothesis.strategies as st

from itertools import product
import tempfile
import subprocess
from io import StringIO

def assert_df_equal(df1, df2):

    if "Strand" in df1 and "Strand" in df2:
        sort_on = "Chromosome Start End Strand".split()
        df1.Strand = df1.Strand.astype("object")
        df2.Strand = df2.Strand.astype("object")
    else:
        sort_on = "Chromosome Start End".split()

    if "Strand_b" in df1:
        sort_on += "Start_b End_b Strand_b".split()
        df1.Strand_b = df1.Strand_b.astype("object")
        df2.Strand_b = df2.Strand_b.astype("object")
    elif "Start_b" in df2:
        sort_on += "Start_b End_b".split()

    df1 = df1.sort_values(sort_on)
    df2 = df2.sort_values(sort_on)

    df1 = df1.reset_index(drop=True)
    df2 = df2.reset_index(drop=True)

    df1.Chromosome = df1.Chromosome.astype("object")
    df2.Chromosome = df2.Chromosome.astype("object")

    print("Actual")
    print(df1.to_csv(sep=" "))
    print("Expected")
    print(df2.to_csv(sep=" "))

    print("Actual dtypes")
    print(df1.dtypes)
    print("Expected dtypes")
    print(df2.dtypes)
    # print("dtypes Strand\n", "1",  df1.Strand.dtype, "2", df2.Strand.dtype)
    # print("dtypes Strand\n", df1.Strand.dtype == df2.Strand.dtype)
    # print("dtypes equal\n", df1.dtypes == df2.dtypes)

    print("Actual index")
    print(df1.index)
    print("Expected index")
    print(df2.index)
    print("index equal", df1.index == df2.index)

    pd.testing.assert_frame_equal(df1, df2)

intersection_command = "bedtools intersect -wb {} -a <(sort -k1,1 -k2,2n {}) -b <(sort -k1,1 -k2,2n {})"

max_examples = 600
deadline = None

strandedness = [False]

positions = st.integers(min_value=0, max_value=int(1e7))
small_lengths = st.integers(min_value=1, max_value=int(1e4))

better_df_minsize = 1

chromosomes_small = st.sampled_from(["chr1"])

better_dfs_min_single_chromosome = data_frames(index=range_indexes(min_size=better_df_minsize),
                                               columns=[column("Chromosome", chromosomes_small),
                                                        column("Start", elements=small_lengths),
                                                        column("End", elements=small_lengths)])

dfs = better_dfs_min_single_chromosome

@st.composite
def dfs_min(draw):
    df = draw(dfs)
    df["End"] = df.Start + df.End

    df.End = df.Start + df.End

    return df


@pytest.mark.bedtools
@pytest.mark.parametrize("strandedness", strandedness)
@settings(max_examples=max_examples, deadline=deadline, timeout=unlimited, suppress_health_check=HealthCheck.all())
@given(df=dfs_min(), df2=dfs_min())
def test_intersection(df, df2, strandedness):

    bedtools_strand = {False: "", "same": "-s", "opposite": "-S"}[strandedness]

    # df = df.sort_values(["Start", "End"]) #, ascending=[True, False])
    # df2 = df2.sort_values(["Start", "End"]) #, ascending=[True, False])

    print("queries")
    df = df.sort_values("Start End".split()).reset_index(drop=True)
    print(df)
    print("subject")
    df2 = df2.sort_values("Start End".split()).reset_index(drop=True)
    print(df2)

    with tempfile.TemporaryDirectory() as temp_dir:
        f1 = "{}/f1.bed".format(temp_dir)
        f2 = "{}/f2.bed".format(temp_dir)
        df.to_csv(f1, sep="\t", header=False, index=False)
        df2.to_csv(f2, sep="\t", header=False, index=False)

        cmd = intersection_command.format(bedtools_strand, f1, f2)

        result = subprocess.check_output(cmd, shell=True, executable="/bin/bash").decode()

        bedtools_df = pd.read_table(StringIO(result), header=None, squeeze=True, names="Chromosome Start End".split())

    overlaps = []

    q = SortedList(df.Start.values, df.End.values, df.index.values)
    db = SortedList(df2.Start.values, df2.End.values, df2.index.values)
    q_hits, db_hits = q.find_overlaps(db)
    print("q_hits", q_hits)
    print("db_hits", db_hits)
    result = df2.iloc[db_hits]

    if not result.empty:
        result = result["Chromosome Start End".split()]

    print("result ", result)
    print("bedtools result ", bedtools_df)

    if not bedtools_df.empty:
        assert_df_equal(result, bedtools_df)
    else:
        assert bedtools_df.empty == result.empty
