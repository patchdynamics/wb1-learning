#!/bin/bash
rm slurm*
RES=$(sbatch --array=1-16 -p DGE ./wait.sh)
sbatch --dependency=afterok:${RES##* } ./iamdone.sh
