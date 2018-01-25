#!/usr/bin/env sh 
set -e
./build/tools/caffe train --solver=EnhancedRESPARC_Powerline/cifar10/solver/cifar_solver_0.prototxt $@ 2>&1 | tee EnhancedRESPARC_Powerline/cifar10/traces/solver_0_trace.txt
./build/tools/caffe train --solver=EnhancedRESPARC_Powerline/cifar10/solver/cifar_solver_1.prototxt $@ 2>&1 | tee EnhancedRESPARC_Powerline/cifar10/traces/solver_1_trace.txt
./build/tools/caffe train --solver=EnhancedRESPARC_Powerline/cifar10/solver/cifar_solver_2.prototxt $@ 2>&1 | tee EnhancedRESPARC_Powerline/cifar10/traces/solver_2_trace.txt
./build/tools/caffe train --solver=EnhancedRESPARC_Powerline/cifar10/solver/cifar_solver_3.prototxt $@ 2>&1 | tee EnhancedRESPARC_Powerline/cifar10/traces/solver_3_trace.txt
./build/tools/caffe train --solver=EnhancedRESPARC_Powerline/cifar10/solver/cifar_solver_4.prototxt $@ 2>&1 | tee EnhancedRESPARC_Powerline/cifar10/traces/solver_4_trace.txt
./build/tools/caffe train --solver=EnhancedRESPARC_Powerline/cifar10/solver/cifar_solver_5.prototxt $@ 2>&1 | tee EnhancedRESPARC_Powerline/cifar10/traces/solver_5_trace.txt
