from flask import current_app

from conekt.models.sequences import Sequence

import subprocess
import shlex
import tempfile
import os


class BlastDB:
    @staticmethod
    def create_db():
        """
        Creates a blast database using the settings specified in the app's configuration
        """
        assert current_app.config['BLAST_ENABLED']

        TEMP_DIR = tempfile.mkdtemp()
        CDS_FASTA_PATH = os.path.join(TEMP_DIR, 'cds.fasta')
        PEP_FASTA_PATH = os.path.join(TEMP_DIR, 'pep.fasta')

        Sequence.export_cds(CDS_FASTA_PATH)
        Sequence.export_protein(PEP_FASTA_PATH)

        build_cds_cmd = current_app.config['MAKEBLASTDB_NUCL_CMD'].replace('<IN>', '"' + CDS_FASTA_PATH + '"')
        build_pep_cmd = current_app.config['MAKEBLASTDB_PROT_CMD'].replace('<IN>', '"' + PEP_FASTA_PATH + '"')

        subprocess.call(shlex.split(build_cds_cmd))
        subprocess.call(shlex.split(build_pep_cmd))



