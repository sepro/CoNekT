

__bowtie_build = """#!/bin/bash
#

#$ -N %s
#$ -cwd
#$ -j y
#$ -S /bin/bash
#$ -o OUT_$JOB_NAME.$JOB_ID
#$ -e ERR_$JOB_NAME.$JOB_ID

#email
%s

#
%s
date
hostname
%s ${in} ${out}
date
"""


def bowtie_build_template(name, email, module, bowtie_build_cmd):
    include_email = "" if email is None else "#$ -m bea\n#$ -M " + email
    load_module = "" if module is None else "module load " + module

    return __bowtie_build % (name, include_email, load_module, bowtie_build_cmd)
