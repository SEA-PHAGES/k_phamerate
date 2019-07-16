""" Unit tests for evaluate functions."""


from classes import Genome
from constants import constants
from pipelines import evaluate
from classes import Ticket
import unittest



class TestEvaluateClass(unittest.TestCase):


    def setUp(self):

        self.null_set = constants.EMPTY_SET
        self.type_set = constants.TICKET_TYPE_SET
        self.run_mode_set = constants.RUN_MODE_SET

        self.add_ticket1 = Ticket.GenomeTicket()
        self.add_ticket1.type = "add"
        self.add_ticket1.primary_phage_id = "Trixie_Draft"
        self.add_ticket1.run_mode = "phagesdb"
        self.add_ticket1.description_field = "product"
        self.add_ticket1.host = "Mycobacterium smegmatis"
        self.add_ticket1.cluster = "A"
        self.add_ticket1.subcluster = "A2"
        self.add_ticket1.status = "final"
        self.add_ticket1.annotation_author = "hatfull"
        self.add_ticket1.annotation_qc = 1
        self.add_ticket1.retrieve_record = 1
        self.add_ticket1.accession = "ABC123.1"
        self.add_ticket1.secondary_phage_id = "none"


    def test_check_ticket_structure_1(self):
        """Verify no error is produced with a correctly structured
        'add' ticket."""
        evaluate.check_ticket_structure(
            self.add_ticket1, self.type_set, self.null_set, self.run_mode_set)

        errors = 0
        for eval in self.add_ticket1.evaluations:
            if eval.status == "error":
                errors += 1
        with self.subTest():
            self.assertEqual(len(self.add_ticket1.evaluations), 9)
        with self.subTest():
            self.assertEqual(errors, 0)


    def test_check_ticket_structure_2(self):
        """Verify an error is produced with an incorrectly structured
        'invalid' ticket 'type' field."""

        ticket = self.add_ticket1
        ticket.type = "invalid"
        evaluate.check_ticket_structure(
            ticket, self.type_set, self.null_set, self.run_mode_set)
        errors = 0
        for eval in ticket.evaluations:
            if eval.status == "error":
                errors += 1
        with self.subTest():
            self.assertEqual(len(ticket.evaluations), 1)
        with self.subTest():
            self.assertEqual(errors, 1)


    def test_check_ticket_structure_3(self):
        """Verify an error is produced with an incorrectly structured
        'add' ticket 'primary_phage_id' field."""

        ticket = self.add_ticket1
        ticket.primary_phage_id = "none"
        evaluate.check_ticket_structure(
            ticket, self.type_set, self.null_set, self.run_mode_set)
        errors = 0
        for eval in ticket.evaluations:
            if eval.status == "error":
                errors += 1
        with self.subTest():
            self.assertEqual(len(ticket.evaluations), 9)
        with self.subTest():
            self.assertEqual(errors, 1)


    def test_check_ticket_structure_4(self):
        """Verify an error is produced with an incorrectly structured
        'add' ticket 'host' field."""

        ticket = self.add_ticket1
        ticket.host = "none"
        evaluate.check_ticket_structure(
            ticket, self.type_set, self.null_set, self.run_mode_set)
        errors = 0
        for eval in ticket.evaluations:
            if eval.status == "error":
                errors += 1
        with self.subTest():
            self.assertEqual(len(ticket.evaluations), 9)
        with self.subTest():
            self.assertEqual(errors, 1)


    def test_check_ticket_structure_5(self):
        """Verify an error is produced with an incorrectly structured
        'add' ticket 'cluster' field."""

        ticket = self.add_ticket1
        ticket.cluster = "none"
        evaluate.check_ticket_structure(
            ticket, self.type_set, self.null_set, self.run_mode_set)
        errors = 0
        for eval in ticket.evaluations:
            if eval.status == "error":
                errors += 1
        with self.subTest():
            self.assertEqual(len(ticket.evaluations), 9)
        with self.subTest():
            self.assertEqual(errors, 1)


    def test_check_ticket_structure_6(self):
        """Verify an error is produced with an incorrectly structured
        'add' ticket 'status' field."""

        ticket = self.add_ticket1
        ticket.status = "none"
        evaluate.check_ticket_structure(
            ticket, self.type_set, self.null_set, self.run_mode_set)
        errors = 0
        for eval in ticket.evaluations:
            if eval.status == "error":
                errors += 1
        with self.subTest():
            self.assertEqual(len(ticket.evaluations), 9)
        with self.subTest():
            self.assertEqual(errors, 1)


    def test_check_ticket_structure_7(self):
        """Verify an error is produced with an incorrectly structured
        'add' ticket 'description_field' field."""

        ticket = self.add_ticket1
        ticket.description_field = "none"
        evaluate.check_ticket_structure(
            ticket, self.type_set, self.null_set, self.run_mode_set)
        errors = 0
        for eval in ticket.evaluations:
            if eval.status == "error":
                errors += 1
        with self.subTest():
            self.assertEqual(len(ticket.evaluations), 9)
        with self.subTest():
            self.assertEqual(errors, 1)


    def test_check_ticket_structure_8(self):
        """Verify an error is produced with an incorrectly structured
        'add' ticket 'annotation_author' field."""

        ticket = self.add_ticket1
        ticket.annotation_author = "none"
        evaluate.check_ticket_structure(
            ticket, self.type_set, self.null_set, self.run_mode_set)
        errors = 0
        for eval in ticket.evaluations:
            if eval.status == "error":
                errors += 1
        with self.subTest():
            self.assertEqual(len(ticket.evaluations), 9)
        with self.subTest():
            self.assertEqual(errors, 1)


    def test_check_ticket_structure_9(self):
        """Verify an error is produced with an incorrectly structured
        'add' ticket 'run_mode' field."""

        ticket = self.add_ticket1
        ticket.run_mode = "invalid"
        evaluate.check_ticket_structure(
            ticket, self.type_set, self.null_set, self.run_mode_set)
        errors = 0
        for eval in ticket.evaluations:
            if eval.status == "error":
                errors += 1
        with self.subTest():
            self.assertEqual(len(ticket.evaluations), 9)
        with self.subTest():
            self.assertEqual(errors, 1)


    def test_check_ticket_structure_10(self):
        """Verify an error is produced with an incorrectly structured
        'add' ticket 'secondary_phage_id' field."""

        ticket = self.add_ticket1
        ticket.secondary_phage_id = "L5"
        evaluate.check_ticket_structure(
            ticket, self.type_set, self.null_set, self.run_mode_set)
        errors = 0
        for eval in ticket.evaluations:
            if eval.status == "error":
                errors += 1
        with self.subTest():
            self.assertEqual(len(ticket.evaluations), 9)
        with self.subTest():
            self.assertEqual(errors, 1)


    def test_check_ticket_structure_11(self):
        """Verify no error is produced with a correctly structured
        'replace' ticket."""

        ticket = self.add_ticket1
        ticket.type = "replace"
        ticket.secondary_phage_id = "L5"
        evaluate.check_ticket_structure(
            ticket, self.type_set, self.null_set, self.run_mode_set)
        errors = 0
        for eval in ticket.evaluations:
            if eval.status == "error":
                errors += 1
        with self.subTest():
            self.assertEqual(len(ticket.evaluations), 9)
        with self.subTest():
            self.assertEqual(errors, 0)


    def test_check_ticket_structure_12(self):
        """Verify an error is produced with an incorrectly structured
        'replace' ticket 'secondary_phage_id' field."""

        ticket = self.add_ticket1
        ticket.type = "replace"
        ticket.secondary_phage_id = "none"
        evaluate.check_ticket_structure(
            ticket, self.type_set, self.null_set, self.run_mode_set)
        errors = 0
        for eval in ticket.evaluations:
            if eval.status == "error":
                errors += 1
        with self.subTest():
            self.assertEqual(len(ticket.evaluations), 9)
        with self.subTest():
            self.assertEqual(errors, 1)













    ###Below = pasted from test.Ticket.py, since some Ticket methods
    ###were moved to evaluate.py. These will now probably need to be implemented
    # in the 'compare_add_replace_ticket()'' evaluate functions.
    #
    # def test_check_update_ticket_1(self):
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.update_ticket.check_update_ticket(phage_id_set)
    #     self.assertEqual(self.update_ticket.evaluations[0].status, "correct")
    #
    # def test_check_update_ticket_2(self):
    #     """Primary Phage ID not in set."""
    #     phage_id_set = set(["L5","RedRock"])
    #     self.update_ticket.check_update_ticket(phage_id_set)
    #     self.assertEqual(self.update_ticket.evaluations[0].status, "error")
    #
    # def test_check_update_ticket_3(self):
    #     """Host is none."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.update_ticket.host = "none"
    #     self.update_ticket.check_update_ticket(phage_id_set)
    #     self.assertEqual(self.update_ticket.evaluations[1].status, "error")
    #
    # def test_check_update_ticket_4(self):
    #     """Cluster is none."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.update_ticket.cluster = "none"
    #     self.update_ticket.check_update_ticket(phage_id_set)
    #     self.assertEqual(self.update_ticket.evaluations[2].status, "error")
    #
    # def test_check_update_ticket_5(self):
    #     """Status is none."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.update_ticket.status = "none"
    #     self.update_ticket.check_update_ticket(phage_id_set)
    #     self.assertEqual(self.update_ticket.evaluations[3].status, "error")
    #
    # def test_check_update_ticket_6(self):
    #     """Description Field is not none."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.update_ticket.description_field = "Product"
    #     self.update_ticket.check_update_ticket(phage_id_set)
    #     self.assertEqual(self.update_ticket.evaluations[4].status, "error")
    #
    # def test_check_update_ticket_7(self):
    #     """Secondary Phage ID is not none."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.update_ticket.secondary_phage_id = "Trixie"
    #     self.update_ticket.check_update_ticket(phage_id_set)
    #     self.assertEqual(self.update_ticket.evaluations[5].status, "error")
    #
    # def test_check_update_ticket_8(self):
    #     """Annotation Author is 0."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.update_ticket.annotation_author = "0"
    #     self.update_ticket.check_update_ticket(phage_id_set)
    #     self.assertEqual(self.update_ticket.evaluations[6].status, "correct")
    #
    # def test_check_update_ticket_9(self):
    #     """Annotation Author is not 1 or 0."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.update_ticket.annotation_author = "none"
    #     self.update_ticket.check_update_ticket(phage_id_set)
    #     self.assertEqual(self.update_ticket.evaluations[6].status, "error")
    #
    # def test_check_update_ticket_10(self):
    #     """Run Mode is not none."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.update_ticket.run_mode = "phagesdb"
    #     self.update_ticket.check_update_ticket(phage_id_set)
    #     self.assertEqual(self.update_ticket.evaluations[7].status, "error")
    #






    #
    # def test_check_add_ticket_1(self):
    #     """Standard add ticket."""
    #     phage_id_set = set(["L5","RedRock"])
    #     self.add_ticket.check_add_ticket(phage_id_set)
    #     self.assertEqual(len(self.add_ticket.evaluations), 0)
    #
    # def test_check_add_ticket_2(self):
    #     """Primary Phage ID already present."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.add_ticket.check_add_ticket(phage_id_set)
    #     self.assertEqual(len(self.add_ticket.evaluations), 1)
    #
    # def test_check_add_ticket_3(self):
    #     """Primary Phage ID is none."""
    #     phage_id_set = set(["L5","RedRock"])
    #     self.add_ticket.primary_phage_id = "none"
    #     self.add_ticket.check_add_ticket(phage_id_set)
    #     self.assertEqual(len(self.add_ticket.evaluations), 1)
    #
    # def test_check_add_ticket_4(self):
    #     """Host is none."""
    #     phage_id_set = set(["L5","RedRock"])
    #     self.add_ticket.host = "none"
    #     self.add_ticket.check_add_ticket(phage_id_set)
    #     self.assertEqual(len(self.add_ticket.evaluations), 1)
    #
    # def test_check_add_ticket_5(self):
    #     """Cluster is none."""
    #     phage_id_set = set(["L5","RedRock"])
    #     self.add_ticket.cluster = "none"
    #     self.add_ticket.check_add_ticket(phage_id_set)
    #     self.assertEqual(len(self.add_ticket.evaluations), 1)
    #
    # def test_check_add_ticket_6(self):
    #     """Status is none."""
    #     phage_id_set = set(["L5","RedRock"])
    #     self.add_ticket.status = "none"
    #     self.add_ticket.check_add_ticket(phage_id_set)
    #     self.assertEqual(len(self.add_ticket.evaluations), 1)
    #
    # def test_check_add_ticket_7(self):
    #     """Status is Final."""
    #     phage_id_set = set(["L5","RedRock"])
    #     self.add_ticket.status = "final"
    #     self.add_ticket.check_add_ticket(phage_id_set)
    #     self.assertEqual(len(self.add_ticket.evaluations), 1)
    #
    # def test_check_add_ticket_8(self):
    #     """Description Field is none."""
    #     phage_id_set = set(["L5","RedRock"])
    #     self.add_ticket.description_field = "none"
    #     self.add_ticket.check_add_ticket(phage_id_set)
    #     self.assertEqual(len(self.add_ticket.evaluations), 1)
    #
    # def test_check_add_ticket_9(self):
    #     """Secondary Phage ID is not none."""
    #     phage_id_set = set(["L5","RedRock"])
    #     self.add_ticket.secondary_phage_id = "Trixie"
    #     self.add_ticket.check_add_ticket(phage_id_set)
    #     self.assertEqual(len(self.add_ticket.evaluations), 1)
    #
    # def test_check_add_ticket_10(self):
    #     """Annotation Author is 0."""
    #     phage_id_set = set(["L5","RedRock"])
    #     self.add_ticket.annotation_author = "0"
    #     self.add_ticket.check_add_ticket(phage_id_set)
    #     self.assertEqual(len(self.add_ticket.evaluations), 0)
    #
    # def test_check_add_ticket_11(self):
    #     """Annotation Author is not 1 or 0."""
    #     phage_id_set = set(["L5","RedRock"])
    #     self.add_ticket.annotation_author = "none"
    #     self.add_ticket.check_add_ticket(phage_id_set)
    #     self.assertEqual(len(self.add_ticket.evaluations), 1)
    #
    # def test_check_add_ticket_12(self):
    #     """Run Mode is none."""
    #     phage_id_set = set(["L5","RedRock"])
    #     self.add_ticket.run_mode = "none"
    #     self.add_ticket.check_add_ticket(phage_id_set)
    #     self.assertEqual(len(self.add_ticket.evaluations), 1)
    #
    #
    #
    #
    #
    #
    #
    #
    # def test_check_remove_ticket_1(self):
    #     """Standard remove ticket."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.remove_ticket.check_remove_ticket(phage_id_set)
    #     self.assertEqual(len(self.remove_ticket.evaluations), 0)
    #
    # def test_check_remove_ticket_2(self):
    #     """Primary Phage ID is not none."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.remove_ticket.primary_phage_id = "Trixie"
    #     self.remove_ticket.check_remove_ticket(phage_id_set)
    #     self.assertEqual(len(self.remove_ticket.evaluations), 1)
    #
    # def test_check_remove_ticket_3(self):
    #     """Host is not none."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.remove_ticket.host = "Mycobacterium"
    #     self.remove_ticket.check_remove_ticket(phage_id_set)
    #     self.assertEqual(len(self.remove_ticket.evaluations), 1)
    #
    # def test_check_remove_ticket_4(self):
    #     """Cluster is not none."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.remove_ticket.cluster = "A"
    #     self.remove_ticket.check_remove_ticket(phage_id_set)
    #     self.assertEqual(len(self.remove_ticket.evaluations), 1)
    #
    # def test_check_remove_ticket_5(self):
    #     """Subcluster is not none."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.remove_ticket.subcluster = "A2"
    #     self.remove_ticket.check_remove_ticket(phage_id_set)
    #     self.assertEqual(len(self.remove_ticket.evaluations), 1)
    #
    # def test_check_remove_ticket_6(self):
    #     """Status is not none."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.remove_ticket.status = "final"
    #     self.remove_ticket.check_remove_ticket(phage_id_set)
    #     self.assertEqual(len(self.remove_ticket.evaluations), 1)
    #
    # def test_check_remove_ticket_7(self):
    #     """Description Field is not none."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.remove_ticket.description_field = "Product"
    #     self.remove_ticket.check_remove_ticket(phage_id_set)
    #     self.assertEqual(len(self.remove_ticket.evaluations), 1)
    #
    # def test_check_remove_ticket_8(self):
    #     """Accession is not none."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.remove_ticket.accession = "ABC123"
    #     self.remove_ticket.check_remove_ticket(phage_id_set)
    #     self.assertEqual(len(self.remove_ticket.evaluations), 1)
    #
    # def test_check_remove_ticket_9(self):
    #     """Annotation Author is not none."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.remove_ticket.annotation_author = "1"
    #     self.remove_ticket.check_remove_ticket(phage_id_set)
    #     self.assertEqual(len(self.remove_ticket.evaluations), 1)
    #
    # def test_check_remove_ticket_10(self):
    #     """Run Mode is not none."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.remove_ticket.run_mode = "phagesdb"
    #     self.remove_ticket.check_remove_ticket(phage_id_set)
    #     self.assertEqual(len(self.remove_ticket.evaluations), 1)
    #
    # def test_check_remove_ticket_11(self):
    #     """Secondary Phage ID is not present."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.remove_ticket.secondary_phage_id = "D29"
    #     self.remove_ticket.check_remove_ticket(phage_id_set)
    #     self.assertEqual(len(self.remove_ticket.evaluations), 1)
    #
    #
    #
    #
    #
    #
    #
    #
    #
    # def test_check_replace_ticket_1(self):
    #     """Standard replace ticket."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.replace_ticket.check_replace_ticket(phage_id_set)
    #     self.assertEqual(len(self.replace_ticket.evaluations), 0)
    #
    # def test_check_replace_ticket_2(self):
    #     """Primary Phage ID is none."""
    #     phage_id_set = set(["Trixie","L5","RedRock","none"])
    #     self.replace_ticket.primary_phage_id = "none"
    #     self.replace_ticket.secondary_phage_id = "none"
    #     self.replace_ticket.check_replace_ticket(phage_id_set)
    #     self.assertEqual(len(self.replace_ticket.evaluations), 1)
    #
    # def test_check_replace_ticket_3(self):
    #     """Primary Phage ID not present and different from Secondary Phage ID."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.replace_ticket.primary_phage_id = "D29"
    #     self.replace_ticket.secondary_phage_id = "L5"
    #     self.replace_ticket.check_replace_ticket(phage_id_set)
    #     self.assertEqual(len(self.replace_ticket.evaluations), 1)
    #
    # def test_check_replace_ticket_4(self):
    #     """Primary Phage ID is present and different from Secondary Phage ID."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.replace_ticket.secondary_phage_id = "L5"
    #     self.replace_ticket.check_replace_ticket(phage_id_set)
    #     self.assertEqual(len(self.replace_ticket.evaluations), 2)
    #
    # def test_check_replace_ticket_5(self):
    #     """Host is none."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.replace_ticket.host = "none"
    #     self.replace_ticket.check_replace_ticket(phage_id_set)
    #     self.assertEqual(len(self.replace_ticket.evaluations), 1)
    #
    # def test_check_replace_ticket_6(self):
    #     """Cluster is none."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.replace_ticket.cluster = "none"
    #     self.replace_ticket.check_replace_ticket(phage_id_set)
    #     self.assertEqual(len(self.replace_ticket.evaluations), 1)
    #
    # def test_check_replace_ticket_7(self):
    #     """Status is none."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.replace_ticket.status = "none"
    #     self.replace_ticket.check_replace_ticket(phage_id_set)
    #     self.assertEqual(len(self.replace_ticket.evaluations), 1)
    #
    # def test_check_replace_ticket_8(self):
    #     """Description Field is none."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.replace_ticket.description_field = "none"
    #     self.replace_ticket.check_replace_ticket(phage_id_set)
    #     self.assertEqual(len(self.replace_ticket.evaluations), 1)
    #
    # def test_check_replace_ticket_9(self):
    #     """Secondary Phage ID is not present."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.replace_ticket.primary_phage_id = "D29"
    #     self.replace_ticket.secondary_phage_id = "D29"
    #     self.replace_ticket.check_replace_ticket(phage_id_set)
    #     self.assertEqual(len(self.replace_ticket.evaluations), 1)
    #
    # def test_check_replace_ticket_10(self):
    #     """Annotation Author is 0."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.replace_ticket.annotation_author = "0"
    #     self.replace_ticket.check_replace_ticket(phage_id_set)
    #     self.assertEqual(len(self.replace_ticket.evaluations), 0)
    #
    # def test_check_replace_ticket_11(self):
    #     """Annotation Author is not 1 or 0."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.replace_ticket.annotation_author = "none"
    #     self.replace_ticket.check_replace_ticket(phage_id_set)
    #     self.assertEqual(len(self.replace_ticket.evaluations), 1)
    #
    # def test_check_replace_ticket_12(self):
    #     """Run Mode is none."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.replace_ticket.run_mode = "none"
    #     self.replace_ticket.check_replace_ticket(phage_id_set)
    #     self.assertEqual(len(self.replace_ticket.evaluations), 1)
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    # def test_check_ticket_1(self):
    #     """Check standard update ticket."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.update_ticket.check_ticket(phage_id_set)
    #     self.assertEqual(len(self.update_ticket.evaluations), 0)
    #
    # def test_check_ticket_2(self):
    #     """Check update ticket with Primary Phage ID not present."""
    #     phage_id_set = set(["L5","RedRock"])
    #     self.update_ticket.check_ticket(phage_id_set)
    #     self.assertEqual(len(self.update_ticket.evaluations), 1)
    #
    # def test_check_ticket_3(self):
    #     """Check standard add ticket."""
    #     phage_id_set = set(["L5","RedRock"])
    #     self.add_ticket.check_ticket(phage_id_set)
    #     self.assertEqual(len(self.add_ticket.evaluations), 0)
    #
    # def test_check_ticket_4(self):
    #     """Check add ticket with Primary Phage ID already present."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.add_ticket.check_ticket(phage_id_set)
    #     self.assertEqual(len(self.add_ticket.evaluations), 1)
    #
    # def test_check_ticket_5(self):
    #     """Check standard remove ticket."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.remove_ticket.check_ticket(phage_id_set)
    #     self.assertEqual(len(self.remove_ticket.evaluations), 0)
    #
    # def test_check_ticket_6(self):
    #     """Check remove ticket with Primary Phage ID not none."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.remove_ticket.primary_phage_id = "Trixie"
    #     self.remove_ticket.check_ticket(phage_id_set)
    #     self.assertEqual(len(self.remove_ticket.evaluations), 1)
    #
    # def test_check_ticket_7(self):
    #     """Check standard replace ticket."""
    #     phage_id_set = set(["Trixie","L5","RedRock"])
    #     self.replace_ticket.check_ticket(phage_id_set)
    #     self.assertEqual(len(self.replace_ticket.evaluations), 0)
    #
    # def test_check_ticket_8(self):
    #     """Check replace ticket when Primary Phage ID is none."""
    #     phage_id_set = set(["Trixie","L5","RedRock","none"])
    #     self.replace_ticket.primary_phage_id = "none"
    #     self.replace_ticket.secondary_phage_id = "none"
    #     self.replace_ticket.check_ticket(phage_id_set)
    #     self.assertEqual(len(self.replace_ticket.evaluations), 1)
    #
    # def test_check_ticket_9(self):
    #     """Check non-standard type of ticket."""
    #     phage_id_set = set(["L5","RedRock"])
    #     self.update_ticket.type = "other"
    #     self.update_ticket.check_ticket(phage_id_set)
    #     self.assertEqual(len(self.update_ticket.evaluations), 0)
    #
    ###Above = pasted from test.Ticket.py, since some Ticket methods
    ###were moved to evaluate.py











class TestEvaluateClass2(unittest.TestCase):


    def setUp(self):
        self.genome = Genome.Genome()
        self.genome.phage_id = "Trixie"
        self.genome.phage_name = "Trixie_Draft"
        self.genome.host = "Mycobacterium"
        self.genome.cluster = "A"
        self.genome.subcluster = "A2"
        self.genome.accession = "ABC123"
        self.genome.filename = "Trixie.gb"
        self.genome.record = "abcd"
        self.genome.sequence = "ATCG"

        self.null_set = set([""])




    def test_check_phagesdb_genome_1(self):
        """Verify no error is produced with a correctly structured
        PhagesDB genome."""

        evaluate.check_phagesdb_genome(self.genome, self.null_set)
        errors = 0
        for eval in self.genome.evaluations:
            if eval.status == "error":
                errors += 1
        with self.subTest():
            self.assertEqual(len(self.genome.evaluations), 9)
        with self.subTest():
            self.assertEqual(errors, 0)

    def test_check_phagesdb_genome_2(self):
        """Verify an error is produced with a PhagesDB genome with
        no phage_id."""

        self.genome.phage_id = ""
        evaluate.check_phagesdb_genome(self.genome, self.null_set)
        errors = 0
        for eval in self.genome.evaluations:
            if eval.status == "error":
                errors += 1
        self.assertEqual(errors, 1)


    def test_check_phagesdb_genome_3(self):
        """Verify an error is produced with a PhagesDB genome with
        no phage_name."""

        self.genome.phage_name = ""
        evaluate.check_phagesdb_genome(self.genome, self.null_set)
        errors = 0
        for eval in self.genome.evaluations:
            if eval.status == "error":
                errors += 1
        self.assertEqual(errors, 1)


    def test_check_phagesdb_genome_4(self):
        """Verify an error is produced with a PhagesDB genome with
        no host."""

        self.genome.host = ""
        evaluate.check_phagesdb_genome(self.genome, self.null_set)
        errors = 0
        for eval in self.genome.evaluations:
            if eval.status == "error":
                errors += 1
        self.assertEqual(errors, 1)


    def test_check_phagesdb_genome_5(self):
        """Verify an error is produced with a PhagesDB genome with
        no cluster."""

        self.genome.cluster = ""
        evaluate.check_phagesdb_genome(self.genome, self.null_set)
        errors = 0
        for eval in self.genome.evaluations:
            if eval.status == "error":
                errors += 1
        self.assertEqual(errors, 1)


    def test_check_phagesdb_genome_6(self):
        """Verify an error is produced with a PhagesDB genome with
        no subcluster."""

        self.genome.subcluster = ""
        evaluate.check_phagesdb_genome(self.genome, self.null_set)
        errors = 0
        for eval in self.genome.evaluations:
            if eval.status == "error":
                errors += 1
        self.assertEqual(errors, 1)


    def test_check_phagesdb_genome_7(self):
        """Verify an error is produced with a PhagesDB genome with
        no accession."""

        self.genome.accession = ""
        evaluate.check_phagesdb_genome(self.genome, self.null_set)
        errors = 0
        for eval in self.genome.evaluations:
            if eval.status == "error":
                errors += 1
        self.assertEqual(errors, 1)


    def test_check_phagesdb_genome_8(self):
        """Verify an error is produced with a PhagesDB genome with
        no filename."""

        self.genome.filename = ""
        evaluate.check_phagesdb_genome(self.genome, self.null_set)
        errors = 0
        for eval in self.genome.evaluations:
            if eval.status == "error":
                errors += 1
        self.assertEqual(errors, 1)


    def test_check_phagesdb_genome_9(self):
        """Verify an error is produced with a PhagesDB genome with
        no record."""

        self.genome.record = ""
        evaluate.check_phagesdb_genome(self.genome, self.null_set)
        errors = 0
        for eval in self.genome.evaluations:
            if eval.status == "error":
                errors += 1
        self.assertEqual(errors, 1)


    def test_check_phagesdb_genome_10(self):
        """Verify an error is produced with a PhagesDB genome with
        no sequence."""

        self.genome.sequence = ""
        evaluate.check_phagesdb_genome(self.genome, self.null_set)
        errors = 0
        for eval in self.genome.evaluations:
            if eval.status == "error":
                errors += 1
        self.assertEqual(errors, 1)






if __name__ == '__main__':
    unittest.main()
