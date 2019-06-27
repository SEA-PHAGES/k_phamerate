""" Unit tests for misc. functions that interact with
GenBank-formatted flat files."""


import unittest
from functions import flat_files
from classes import Cds
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation, CompoundLocation
from Bio.SeqFeature import ExactPosition

class TestFlatFileFunctions(unittest.TestCase):


    def setUp(self):
        self.cds = Cds.CdsFeature()




    def test_parse_coordinates_1(self):
        """Verify non-compound location is parsed correctly."""

        seqfeature = SeqFeature(FeatureLocation( \
            ExactPosition(2), ExactPosition(10)), \
            type = "CDS", \
            strand = 1)

        output_left, output_right, parts, output_eval = \
            flat_files.parse_coordinates(seqfeature)

        exp_left = 2
        exp_right = 10
        exp_parts = 1

        with self.subTest():
            self.assertEqual(output_left, exp_left)
        with self.subTest():
            self.assertEqual(output_right, exp_right)
        with self.subTest():
            self.assertEqual(parts, exp_parts)
        with self.subTest():
            self.assertIsNone(output_eval)


    def test_parse_coordinates_2(self):
        """Verify 1 strand 2-part compound location is parsed correctly."""

        seqfeature = SeqFeature(CompoundLocation( \
            [FeatureLocation( \
                ExactPosition(2), ExactPosition(10)), \
            FeatureLocation( \
                ExactPosition(8), ExactPosition(20))]), \
            type = "CDS", \
            strand = 1)

        output_left, output_right, parts, output_eval = \
            flat_files.parse_coordinates(seqfeature)

        exp_left = 2
        exp_right = 20
        exp_parts = 2

        with self.subTest():
            self.assertEqual(output_left, exp_left)
        with self.subTest():
            self.assertEqual(output_right, exp_right)
        with self.subTest():
            self.assertEqual(parts, exp_parts)
        with self.subTest():
            self.assertIsNone(output_eval)


    def test_parse_coordinates_3(self):
        """Verify -1 strand 2-part compound location is parsed correctly."""

        seqfeature = SeqFeature(CompoundLocation( \
            [FeatureLocation( \
                ExactPosition(2), ExactPosition(10)), \
            FeatureLocation( \
                ExactPosition(8), ExactPosition(20))]), \
            type = "CDS", \
            strand = -1)

        output_left, output_right, parts, output_eval = \
            flat_files.parse_coordinates(seqfeature)

        exp_left = 8
        exp_right = 10
        exp_parts = 2

        with self.subTest():
            self.assertEqual(output_left, exp_left)
        with self.subTest():
            self.assertEqual(output_right, exp_right)
        with self.subTest():
            self.assertEqual(parts, exp_parts)
        with self.subTest():
            self.assertIsNone(output_eval)


    def test_parse_coordinates_4(self):
        """Verify undefined strand 2-part compound location is not parsed."""

        seqfeature = SeqFeature(CompoundLocation( \
            [FeatureLocation( \
                ExactPosition(2), ExactPosition(10)), \
            FeatureLocation( \
                ExactPosition(8), ExactPosition(20))]), \
            type = "CDS", \
            strand = None)

        output_left, output_right, parts, output_eval = \
            flat_files.parse_coordinates(seqfeature)

        exp_left = -1
        exp_right = 0
        exp_parts = 0

        with self.subTest():
            self.assertEqual(output_left, exp_left)
        with self.subTest():
            self.assertEqual(output_right, exp_right)
        with self.subTest():
            self.assertEqual(parts, exp_parts)
        with self.subTest():
            self.assertIsNotNone(output_eval)


    def test_parse_coordinates_5(self):
        """Verify 1 strand 3-part compound location is not parsed."""

        seqfeature = SeqFeature(CompoundLocation( \
            [FeatureLocation( \
                ExactPosition(2), ExactPosition(10)), \
            FeatureLocation( \
                ExactPosition(8), ExactPosition(20)), \
            FeatureLocation( \
                ExactPosition(30), ExactPosition(50))]), \
            type = "CDS", \
            strand = 1)

        output_left, output_right, parts, output_eval = \
            flat_files.parse_coordinates(seqfeature)

        exp_left = -1
        exp_right = 0
        exp_parts = 3

        with self.subTest():
            self.assertEqual(output_left, exp_left)
        with self.subTest():
            self.assertEqual(output_right, exp_right)
        with self.subTest():
            self.assertEqual(parts, exp_parts)
        with self.subTest():
            self.assertIsNotNone(output_eval)


    def test_parse_coordinates_6(self):
        """Verify location of invalid data type is not parsed."""

        seqfeature = SeqFeature(None, type = "CDS", strand = None)

        output_left, output_right, parts, output_eval = \
            flat_files.parse_coordinates(seqfeature)

        exp_left = -1
        exp_right = 0
        exp_parts = 0

        with self.subTest():
            self.assertEqual(output_left, exp_left)
        with self.subTest():
            self.assertEqual(output_right, exp_right)
        with self.subTest():
            self.assertEqual(parts, exp_parts)
        with self.subTest():
            self.assertIsNotNone(output_eval)






    def test_parse_cds_feature_1(self):
        """Verify CDS features is parsed."""
        qualifier_dict = {"locus_tag": ["SEA_L5_1"], \
                            "translation": ["ABCDE"], \
                            "transl_table": ["11"], \
                            "product": [" unknown "], \
                            "function": [" hypothetical protein "], \
                            "note": [" gp5 "], \
                            "gene": ["1"]}

        seqfeature = SeqFeature(FeatureLocation( \
                    ExactPosition(2), ExactPosition(10)), \
                    type = "CDS", \
                    strand = 1, \
                    qualifiers = qualifier_dict)

        eval_result = flat_files.parse_cds_feature(self.cds, seqfeature)

        with self.subTest():
            self.assertEqual(self.cds.type_id, "CDS")
        with self.subTest():
            self.assertEqual(self.cds.locus_tag, "SEA_L5_1")
        with self.subTest():
            self.assertEqual(self.cds.strand, "F")
        with self.subTest():
            self.assertEqual(self.cds.left_boundary, 2)
        with self.subTest():
            self.assertEqual(self.cds.right_boundary, 10)
        with self.subTest():
            self.assertEqual(self.cds.compound_parts, 1)
        with self.subTest():
            self.assertIsNone(eval_result)
        with self.subTest():
            self.assertEqual(self.cds.coordinate_format, "0_half_open")
        with self.subTest():
            self.assertEqual(self.cds.translation, "ABCDE")
        with self.subTest():
            self.assertEqual(self.cds._translation_length, 5)
        with self.subTest():
            self.assertEqual(self.cds._nucleotide_length, 9)
        with self.subTest():
            self.assertEqual(self.cds.translation_table, "11")
        with self.subTest():
            self.assertEqual(self.cds.product_description, "unknown")
        with self.subTest():
            self.assertEqual(self.cds.processed_product_description, "")
        with self.subTest():
            self.assertEqual(self.cds.function_description, \
                "hypothetical protein")
        with self.subTest():
            self.assertEqual(self.cds.processed_function_description, "")
        with self.subTest():
            self.assertEqual(self.cds.note_description, "gp5")
        with self.subTest():
            self.assertEqual(self.cds.processed_note_description, "")
        with self.subTest():
            self.assertEqual(self.cds.gene_number, "1")


    def test_parse_cds_feature_2(self):
        """Verify CDS features is parsed with no locus tag."""
        qualifier_dict = {"locus_tag_x": ["SEA_L5_1"], \
                            "translation": ["ABCDE"], \
                            "transl_table": ["11"], \
                            "product": [" unknown "], \
                            "function": [" hypothetical protein "], \
                            "note": [" gp5 "], \
                            "gene": ["1"]}

        seqfeature = SeqFeature(FeatureLocation( \
                    ExactPosition(2), ExactPosition(10)), \
                    type = "CDS", \
                    strand = 1, \
                    qualifiers = qualifier_dict)

        eval_result = flat_files.parse_cds_feature(self.cds, seqfeature)

        with self.subTest():
            self.assertEqual(self.cds.type_id, "CDS")
        with self.subTest():
            self.assertEqual(self.cds.locus_tag, "")
        with self.subTest():
            self.assertEqual(self.cds.strand, "F")
        with self.subTest():
            self.assertEqual(self.cds.left_boundary, 2)
        with self.subTest():
            self.assertEqual(self.cds.right_boundary, 10)
        with self.subTest():
            self.assertEqual(self.cds.compound_parts, 1)
        with self.subTest():
            self.assertIsNone(eval_result)
        with self.subTest():
            self.assertEqual(self.cds.coordinate_format, "0_half_open")
        with self.subTest():
            self.assertEqual(self.cds.translation, "ABCDE")
        with self.subTest():
            self.assertEqual(self.cds._translation_length, 5)
        with self.subTest():
            self.assertEqual(self.cds._nucleotide_length, 9)
        with self.subTest():
            self.assertEqual(self.cds.translation_table, "11")
        with self.subTest():
            self.assertEqual(self.cds.product_description, "unknown")
        with self.subTest():
            self.assertEqual(self.cds.processed_product_description, "")
        with self.subTest():
            self.assertEqual(self.cds.function_description, \
                "hypothetical protein")
        with self.subTest():
            self.assertEqual(self.cds.processed_function_description, "")
        with self.subTest():
            self.assertEqual(self.cds.note_description, "gp5")
        with self.subTest():
            self.assertEqual(self.cds.processed_note_description, "")
        with self.subTest():
            self.assertEqual(self.cds.gene_number, "1")


    def test_parse_cds_feature_3(self):
        """Verify CDS features is parsed with problematic coordinates."""
        qualifier_dict = {"locus_tag": ["SEA_L5_1"], \
                            "translation": ["ABCDE"], \
                            "transl_table": ["11"], \
                            "product": [" unknown "], \
                            "function": [" hypothetical protein "], \
                            "note": [" gp5 "], \
                            "gene": ["1"]}

        seqfeature = SeqFeature(CompoundLocation( \
            [FeatureLocation( \
                ExactPosition(2), ExactPosition(10)), \
            FeatureLocation( \
                ExactPosition(8), ExactPosition(20)), \
            FeatureLocation( \
                ExactPosition(30), ExactPosition(50))]), \
            type = "CDS", \
            strand = 1, \
            qualifiers = qualifier_dict)

        eval_result = flat_files.parse_cds_feature(self.cds, seqfeature)

        with self.subTest():
            self.assertEqual(self.cds.type_id, "CDS")
        with self.subTest():
            self.assertEqual(self.cds.locus_tag, "SEA_L5_1")
        with self.subTest():
            self.assertEqual(self.cds.strand, "F")
        with self.subTest():
            self.assertEqual(self.cds.left_boundary, -1)
        with self.subTest():
            self.assertEqual(self.cds.right_boundary, 0)
        with self.subTest():
            self.assertEqual(self.cds.compound_parts, 3)
        with self.subTest():
            self.assertIsNotNone(eval_result)
        with self.subTest():
            self.assertEqual(self.cds.coordinate_format, "0_half_open")
        with self.subTest():
            self.assertEqual(self.cds.translation, "ABCDE")
        with self.subTest():
            self.assertEqual(self.cds._translation_length, 5)
        with self.subTest():
            self.assertEqual(self.cds._nucleotide_length, 2)
        with self.subTest():
            self.assertEqual(self.cds.translation_table, "11")
        with self.subTest():
            self.assertEqual(self.cds.product_description, "unknown")
        with self.subTest():
            self.assertEqual(self.cds.processed_product_description, "")
        with self.subTest():
            self.assertEqual(self.cds.function_description, \
                "hypothetical protein")
        with self.subTest():
            self.assertEqual(self.cds.processed_function_description, "")
        with self.subTest():
            self.assertEqual(self.cds.note_description, "gp5")
        with self.subTest():
            self.assertEqual(self.cds.processed_note_description, "")
        with self.subTest():
            self.assertEqual(self.cds.gene_number, "1")


    def test_parse_cds_feature_4(self):
        """Verify CDS features is parsed with no translation."""
        qualifier_dict = {"locus_tag": ["SEA_L5_1"], \
                            "translation_x": ["ABCDE"], \
                            "transl_table": ["11"], \
                            "product": [" unknown "], \
                            "function": [" hypothetical protein "], \
                            "note": [" gp5 "], \
                            "gene": ["1"]}

        seqfeature = SeqFeature(FeatureLocation( \
                    ExactPosition(2), ExactPosition(10)), \
                    type = "CDS", \
                    strand = 1, \
                    qualifiers = qualifier_dict)

        eval_result = flat_files.parse_cds_feature(self.cds, seqfeature)

        with self.subTest():
            self.assertEqual(self.cds.type_id, "CDS")
        with self.subTest():
            self.assertEqual(self.cds.locus_tag, "SEA_L5_1")
        with self.subTest():
            self.assertEqual(self.cds.strand, "F")
        with self.subTest():
            self.assertEqual(self.cds.left_boundary, 2)
        with self.subTest():
            self.assertEqual(self.cds.right_boundary, 10)
        with self.subTest():
            self.assertEqual(self.cds.compound_parts, 1)
        with self.subTest():
            self.assertIsNone(eval_result)
        with self.subTest():
            self.assertEqual(self.cds.coordinate_format, "0_half_open")
        with self.subTest():
            self.assertEqual(self.cds.translation, "")
        with self.subTest():
            self.assertEqual(self.cds._translation_length, 0)
        with self.subTest():
            self.assertEqual(self.cds._nucleotide_length, 9)
        with self.subTest():
            self.assertEqual(self.cds.translation_table, "11")
        with self.subTest():
            self.assertEqual(self.cds.product_description, "unknown")
        with self.subTest():
            self.assertEqual(self.cds.processed_product_description, "")
        with self.subTest():
            self.assertEqual(self.cds.function_description, \
                "hypothetical protein")
        with self.subTest():
            self.assertEqual(self.cds.processed_function_description, "")
        with self.subTest():
            self.assertEqual(self.cds.note_description, "gp5")
        with self.subTest():
            self.assertEqual(self.cds.processed_note_description, "")
        with self.subTest():
            self.assertEqual(self.cds.gene_number, "1")


    def test_parse_cds_feature_5(self):
        """Verify CDS features is parsed with no translation table."""
        qualifier_dict = {"locus_tag": ["SEA_L5_1"], \
                            "translation": ["ABCDE"], \
                            "transl_table_x": ["11"], \
                            "product": [" unknown "], \
                            "function": [" hypothetical protein "], \
                            "note": [" gp5 "], \
                            "gene": ["1"]}

        seqfeature = SeqFeature(FeatureLocation( \
                    ExactPosition(2), ExactPosition(10)), \
                    type = "CDS", \
                    strand = 1, \
                    qualifiers = qualifier_dict)

        eval_result = flat_files.parse_cds_feature(self.cds, seqfeature)

        with self.subTest():
            self.assertEqual(self.cds.type_id, "CDS")
        with self.subTest():
            self.assertEqual(self.cds.locus_tag, "SEA_L5_1")
        with self.subTest():
            self.assertEqual(self.cds.strand, "F")
        with self.subTest():
            self.assertEqual(self.cds.left_boundary, 2)
        with self.subTest():
            self.assertEqual(self.cds.right_boundary, 10)
        with self.subTest():
            self.assertEqual(self.cds.compound_parts, 1)
        with self.subTest():
            self.assertIsNone(eval_result)
        with self.subTest():
            self.assertEqual(self.cds.coordinate_format, "0_half_open")
        with self.subTest():
            self.assertEqual(self.cds.translation, "ABCDE")
        with self.subTest():
            self.assertEqual(self.cds._translation_length, 5)
        with self.subTest():
            self.assertEqual(self.cds._nucleotide_length, 9)
        with self.subTest():
            self.assertEqual(self.cds.translation_table, "")
        with self.subTest():
            self.assertEqual(self.cds.product_description, "unknown")
        with self.subTest():
            self.assertEqual(self.cds.processed_product_description, "")
        with self.subTest():
            self.assertEqual(self.cds.function_description, \
                "hypothetical protein")
        with self.subTest():
            self.assertEqual(self.cds.processed_function_description, "")
        with self.subTest():
            self.assertEqual(self.cds.note_description, "gp5")
        with self.subTest():
            self.assertEqual(self.cds.processed_note_description, "")
        with self.subTest():
            self.assertEqual(self.cds.gene_number, "1")


    def test_parse_cds_feature_6(self):
        """Verify CDS features is parsed with no product."""
        qualifier_dict = {"locus_tag": ["SEA_L5_1"], \
                            "translation": ["ABCDE"], \
                            "transl_table": ["11"], \
                            "product_x": [" unknown "], \
                            "function": [" hypothetical protein "], \
                            "note": [" gp5 "], \
                            "gene": ["1"]}

        seqfeature = SeqFeature(FeatureLocation( \
                    ExactPosition(2), ExactPosition(10)), \
                    type = "CDS", \
                    strand = 1, \
                    qualifiers = qualifier_dict)

        eval_result = flat_files.parse_cds_feature(self.cds, seqfeature)

        with self.subTest():
            self.assertEqual(self.cds.type_id, "CDS")
        with self.subTest():
            self.assertEqual(self.cds.locus_tag, "SEA_L5_1")
        with self.subTest():
            self.assertEqual(self.cds.strand, "F")
        with self.subTest():
            self.assertEqual(self.cds.left_boundary, 2)
        with self.subTest():
            self.assertEqual(self.cds.right_boundary, 10)
        with self.subTest():
            self.assertEqual(self.cds.compound_parts, 1)
        with self.subTest():
            self.assertIsNone(eval_result)
        with self.subTest():
            self.assertEqual(self.cds.coordinate_format, "0_half_open")
        with self.subTest():
            self.assertEqual(self.cds.translation, "ABCDE")
        with self.subTest():
            self.assertEqual(self.cds._translation_length, 5)
        with self.subTest():
            self.assertEqual(self.cds._nucleotide_length, 9)
        with self.subTest():
            self.assertEqual(self.cds.translation_table, "11")
        with self.subTest():
            self.assertEqual(self.cds.product_description, "")
        with self.subTest():
            self.assertEqual(self.cds.processed_product_description, "")
        with self.subTest():
            self.assertEqual(self.cds.function_description, \
                "hypothetical protein")
        with self.subTest():
            self.assertEqual(self.cds.processed_function_description, "")
        with self.subTest():
            self.assertEqual(self.cds.note_description, "gp5")
        with self.subTest():
            self.assertEqual(self.cds.processed_note_description, "")
        with self.subTest():
            self.assertEqual(self.cds.gene_number, "1")


    def test_parse_cds_feature_7(self):
        """Verify CDS features is parsed with no function."""
        qualifier_dict = {"locus_tag": ["SEA_L5_1"], \
                            "translation": ["ABCDE"], \
                            "transl_table": ["11"], \
                            "product": [" unknown "], \
                            "function_x": [" hypothetical protein "], \
                            "note": [" gp5 "], \
                            "gene": ["1"]}

        seqfeature = SeqFeature(FeatureLocation( \
                    ExactPosition(2), ExactPosition(10)), \
                    type = "CDS", \
                    strand = 1, \
                    qualifiers = qualifier_dict)

        eval_result = flat_files.parse_cds_feature(self.cds, seqfeature)

        with self.subTest():
            self.assertEqual(self.cds.type_id, "CDS")
        with self.subTest():
            self.assertEqual(self.cds.locus_tag, "SEA_L5_1")
        with self.subTest():
            self.assertEqual(self.cds.strand, "F")
        with self.subTest():
            self.assertEqual(self.cds.left_boundary, 2)
        with self.subTest():
            self.assertEqual(self.cds.right_boundary, 10)
        with self.subTest():
            self.assertEqual(self.cds.compound_parts, 1)
        with self.subTest():
            self.assertIsNone(eval_result)
        with self.subTest():
            self.assertEqual(self.cds.coordinate_format, "0_half_open")
        with self.subTest():
            self.assertEqual(self.cds.translation, "ABCDE")
        with self.subTest():
            self.assertEqual(self.cds._translation_length, 5)
        with self.subTest():
            self.assertEqual(self.cds._nucleotide_length, 9)
        with self.subTest():
            self.assertEqual(self.cds.translation_table, "11")
        with self.subTest():
            self.assertEqual(self.cds.product_description, "unknown")
        with self.subTest():
            self.assertEqual(self.cds.processed_product_description, "")
        with self.subTest():
            self.assertEqual(self.cds.function_description, \
                "")
        with self.subTest():
            self.assertEqual(self.cds.processed_function_description, "")
        with self.subTest():
            self.assertEqual(self.cds.note_description, "gp5")
        with self.subTest():
            self.assertEqual(self.cds.processed_note_description, "")
        with self.subTest():
            self.assertEqual(self.cds.gene_number, "1")


    def test_parse_cds_feature_8(self):
        """Verify CDS features is parsed with no note."""
        qualifier_dict = {"locus_tag": ["SEA_L5_1"], \
                            "translation": ["ABCDE"], \
                            "transl_table": ["11"], \
                            "product": [" unknown "], \
                            "function": [" hypothetical protein "], \
                            "note_x": [" gp5 "], \
                            "gene": ["1"]}

        seqfeature = SeqFeature(FeatureLocation( \
                    ExactPosition(2), ExactPosition(10)), \
                    type = "CDS", \
                    strand = 1, \
                    qualifiers = qualifier_dict)

        eval_result = flat_files.parse_cds_feature(self.cds, seqfeature)

        with self.subTest():
            self.assertEqual(self.cds.type_id, "CDS")
        with self.subTest():
            self.assertEqual(self.cds.locus_tag, "SEA_L5_1")
        with self.subTest():
            self.assertEqual(self.cds.strand, "F")
        with self.subTest():
            self.assertEqual(self.cds.left_boundary, 2)
        with self.subTest():
            self.assertEqual(self.cds.right_boundary, 10)
        with self.subTest():
            self.assertEqual(self.cds.compound_parts, 1)
        with self.subTest():
            self.assertIsNone(eval_result)
        with self.subTest():
            self.assertEqual(self.cds.coordinate_format, "0_half_open")
        with self.subTest():
            self.assertEqual(self.cds.translation, "ABCDE")
        with self.subTest():
            self.assertEqual(self.cds._translation_length, 5)
        with self.subTest():
            self.assertEqual(self.cds._nucleotide_length, 9)
        with self.subTest():
            self.assertEqual(self.cds.translation_table, "11")
        with self.subTest():
            self.assertEqual(self.cds.product_description, "unknown")
        with self.subTest():
            self.assertEqual(self.cds.processed_product_description, "")
        with self.subTest():
            self.assertEqual(self.cds.function_description, \
                "hypothetical protein")
        with self.subTest():
            self.assertEqual(self.cds.processed_function_description, "")
        with self.subTest():
            self.assertEqual(self.cds.note_description, "")
        with self.subTest():
            self.assertEqual(self.cds.processed_note_description, "")
        with self.subTest():
            self.assertEqual(self.cds.gene_number, "1")


    def test_parse_cds_feature_9(self):
        """Verify CDS features is parsed with no gene."""
        qualifier_dict = {"locus_tag": ["SEA_L5_1"], \
                            "translation": ["ABCDE"], \
                            "transl_table": ["11"], \
                            "product": [" unknown "], \
                            "function": [" hypothetical protein "], \
                            "note": [" gp5 "], \
                            "gene_x": ["1"]}

        seqfeature = SeqFeature(FeatureLocation( \
                    ExactPosition(2), ExactPosition(10)), \
                    type = "CDS", \
                    strand = 1, \
                    qualifiers = qualifier_dict)

        eval_result = flat_files.parse_cds_feature(self.cds, seqfeature)

        with self.subTest():
            self.assertEqual(self.cds.type_id, "CDS")
        with self.subTest():
            self.assertEqual(self.cds.locus_tag, "SEA_L5_1")
        with self.subTest():
            self.assertEqual(self.cds.strand, "F")
        with self.subTest():
            self.assertEqual(self.cds.left_boundary, 2)
        with self.subTest():
            self.assertEqual(self.cds.right_boundary, 10)
        with self.subTest():
            self.assertEqual(self.cds.compound_parts, 1)
        with self.subTest():
            self.assertIsNone(eval_result)
        with self.subTest():
            self.assertEqual(self.cds.coordinate_format, "0_half_open")
        with self.subTest():
            self.assertEqual(self.cds.translation, "ABCDE")
        with self.subTest():
            self.assertEqual(self.cds._translation_length, 5)
        with self.subTest():
            self.assertEqual(self.cds._nucleotide_length, 9)
        with self.subTest():
            self.assertEqual(self.cds.translation_table, "11")
        with self.subTest():
            self.assertEqual(self.cds.product_description, "unknown")
        with self.subTest():
            self.assertEqual(self.cds.processed_product_description, "")
        with self.subTest():
            self.assertEqual(self.cds.function_description, \
                "hypothetical protein")
        with self.subTest():
            self.assertEqual(self.cds.processed_function_description, "")
        with self.subTest():
            self.assertEqual(self.cds.note_description, "gp5")
        with self.subTest():
            self.assertEqual(self.cds.processed_note_description, "")
        with self.subTest():
            self.assertEqual(self.cds.gene_number, "")





    def test_create_feature_dictionary_1(self):
        """Verify feature dictionary is constructed correctly with
        one feature."""

        feature_list = [SeqFeature(type = "CDS")]

        feature_dict = flat_files.create_feature_dictionary(feature_list)

        with self.subTest():
            self.assertEqual(len(feature_dict.keys()), 1)
        with self.subTest():
            self.assertEqual(len(feature_dict["CDS"]), 1)


    def test_create_feature_dictionary_2(self):
        """Verify feature dictionary is constructed correctly with
        no features."""

        feature_list = []

        feature_dict = flat_files.create_feature_dictionary(feature_list)

        with self.subTest():
            self.assertEqual(len(feature_dict.keys()), 0)


    def test_create_feature_dictionary_3(self):
        """Verify feature dictionary is constructed correctly with
        several different feature types."""

        feature_list = [ \
            SeqFeature(type = "CDS"), \
            SeqFeature(type = "CDS"), \
            SeqFeature(type = "tRNA"), \
            SeqFeature(type = "tmRNA"), \
            SeqFeature(type = "other"), \
            SeqFeature(type = "gene")]

        feature_dict = flat_files.create_feature_dictionary(feature_list)

        with self.subTest():
            self.assertEqual(len(feature_dict.keys()), 5)
        with self.subTest():
            self.assertEqual(len(feature_dict["CDS"]), 2)
        with self.subTest():
            self.assertEqual(len(feature_dict["tRNA"]), 1)
        with self.subTest():
            self.assertEqual(len(feature_dict["tmRNA"]), 1)
        with self.subTest():
            self.assertEqual(len(feature_dict["other"]), 1)
        with self.subTest():
            self.assertEqual(len(feature_dict["gene"]), 1)













    def test_create_cds_objects_1(self):
        """Verify cds objects list is constructed from empty Biopython
        CDS feature list."""
        biopython_feature_list = []
        cds_object_list = flat_files.create_cds_objects(biopython_feature_list)
        with self.subTest():
            self.assertEqual(len(cds_object_list), 0)

    def test_create_cds_objects_2(self):
        """Verify cds objects list is constructed from list of one Biopython
        CDS features."""

        seqfeature1 = SeqFeature(FeatureLocation( \
                    ExactPosition(2), ExactPosition(10)), \
                    type = "CDS", \
                    strand = 1)

        biopython_feature_list = [seqfeature1]

        cds_object_list = flat_files.create_cds_objects(biopython_feature_list)
        with self.subTest():
            self.assertEqual(len(cds_object_list), 1)



    def test_create_cds_objects_3(self):
        """Verify cds objects list is constructed from list of three Biopython
        CDS features."""

        seqfeature1 = SeqFeature(FeatureLocation( \
                    ExactPosition(2), ExactPosition(10)), \
                    type = "CDS", \
                    strand = 1)


        seqfeature2 = SeqFeature(FeatureLocation( \
                    ExactPosition(50), ExactPosition(80)), \
                    type = "CDS", \
                    strand = -1)


        seqfeature3 = SeqFeature(FeatureLocation( \
                    ExactPosition(5), ExactPosition(6)), \
                    type = "CDS", \
                    strand = 1)

        biopython_feature_list = [seqfeature1, seqfeature2, seqfeature3]

        cds_object_list = flat_files.create_cds_objects(biopython_feature_list)
        with self.subTest():
            self.assertEqual(len(cds_object_list), 3)






    def test_create_cds_objects_4(self):
        """Verify cds objects list is constructed from list of two Biopython
        CDS features when a third has an error."""

        seqfeature1 = SeqFeature(FeatureLocation( \
                    ExactPosition(2), ExactPosition(10)), \
                    type = "CDS", \
                    strand = 1)


        seqfeature2 = SeqFeature(FeatureLocation( \
                    ExactPosition(50), ExactPosition(80)), \
                    type = "CDS", \
                    strand = -1)

        seqfeature3 = SeqFeature(FeatureLocation( \
                    ExactPosition(5), ExactPosition(6)), \
                    type = "CDS", \
                    strand = None)


        biopython_feature_list = [seqfeature1, seqfeature2, seqfeature3]

        cds_object_list = flat_files.create_cds_objects(biopython_feature_list)
        self.assertEqual(len(cds_object_list), 2)













if __name__ == '__main__':
    unittest.main()
