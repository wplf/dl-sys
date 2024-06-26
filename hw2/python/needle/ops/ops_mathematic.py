"""Operator implementations."""

from numbers import Number
from typing import Optional, List, Tuple, Union

from ..autograd import NDArray
from ..autograd import Op, Tensor, Value, TensorOp
from ..autograd import TensorTuple, TensorTupleOp
import numpy

# NOTE: we will import numpy as the array_api
# as the backend for our computations, this line will change in later homeworks

import numpy as array_api


class EWiseAdd(TensorOp):
    def compute(self, a: NDArray, b: NDArray):
        return a + b

    def gradient(self, out_grad: Tensor, node: Tensor):
        return out_grad, out_grad


def add(a, b):
    return EWiseAdd()(a, b)


class AddScalar(TensorOp):
    def __init__(self, scalar):
        self.scalar = scalar

    def compute(self, a: NDArray):
        if self.scalar is None:
            return a
        return a + self.scalar

    def gradient(self, out_grad: Tensor, node: Tensor):
        return (out_grad, )


def add_scalar(a, scalar):
    return AddScalar(scalar)(a)


class EWiseMul(TensorOp):
    def compute(self, a: NDArray, b: NDArray):
        return a * b

    def gradient(self, out_grad: Tensor, node: Tensor):
        lhs, rhs = node.inputs
        return out_grad * rhs, out_grad * lhs


def multiply(a, b):
    return EWiseMul()(a, b)


class MulScalar(TensorOp):
    def __init__(self, scalar):
        self.scalar = scalar

    def compute(self, a: NDArray):
        return a * self.scalar
    def gradient(self, out_grad: Tensor, node: Tensor):
        return (out_grad * self.scalar,)


def mul_scalar(a, scalar):
    return MulScalar(scalar)(a)


class PowerScalar(TensorOp):
    """Op raise a tensor to an (integer) power."""

    def __init__(self, scalar: int):
        self.scalar = scalar

    def compute(self, a: NDArray) -> NDArray:
        ### BEGIN YOUR SOLUTION
        return array_api.power(a, self.scalar)
        # raise NotImplementedError()
        ### END YOUR SOLUTION

    def gradient(self, out_grad, node : Tensor):
        ### BEGIN YOUR SOLUTION
        return (out_grad * (node.inputs[0] ** (self.scalar-1) * self.scalar ), )
        # raise NotImplementedError()
        ### END YOUR SOLUTION


def power_scalar(a, scalar):
    return PowerScalar(scalar)(a)


class EWisePow(TensorOp):
    """Op to element-wise raise a tensor to a power."""

    def compute(self, a: NDArray, b: NDArray) -> NDArray:
        return a**b

    def gradient(self, out_grad, node):
        if not isinstance(node.inputs[0], NDArray) or not isinstance(
            node.inputs[1], NDArray
        ):
            raise ValueError("Both inputs must be tensors (NDArray).")

        a, b = node.inputs[0], node.inputs[1]
        grad_a = out_grad * b * (a ** (b - 1))
        grad_b = out_grad * (a**b) * array_api.log(a.data)
        return grad_a, grad_b

def power(a, b):
    return EWisePow()(a, b)


class EWiseDiv(TensorOp):
    """Op to element-wise divide two nodes."""

    def compute(self, a, b):
        ### BEGIN YOUR SOLUTION
        return a / b
        # raise NotImplementedError()
        ### END YOUR SOLUTION

    def gradient(self, out_grad, node):
        ### BEGIN YOUR SOLUTION
        # if not isinstance(node.inputs[0], NDArray) or not isinstance(
        #     node.inputs[1], NDArray
        # ):
        #     raise ValueError("Both inputs must be tensors (NDArray).")
        a, b = node.inputs[0], node.inputs[1]
        grad_a = out_grad / b
        grad_b = -1 * out_grad * a / b / b
        # breakpoint()
        return (grad_a, grad_b)
        # raise NotImplementedError()
        ### END YOUR SOLUTION


def divide(a, b):
    return EWiseDiv()(a, b)


class DivScalar(TensorOp):
    def __init__(self, scalar):
        self.scalar = scalar

    def compute(self, a):
        ### BEGIN YOUR SOLUTION
        return a / self.scalar
        # raise NotImplementedError()
        ### END YOUR SOLUTION

    def gradient(self, out_grad, node):
        ### BEGIN YOUR SOLUTION
        return (out_grad / self.scalar, )
        # return
        # raise NotImplementedError()
        ### END YOUR SOLUTION


def divide_scalar(a, scalar):
    return DivScalar(scalar)(a)


class Transpose(TensorOp):
    def __init__(self, axes: Optional[tuple] = None):
        self.axes = axes

    def compute(self, a):
        # breakpoint()
        ### BEGIN YOUR SOLUTION
        transpose_axis = array_api.arange(len(a.shape))
        if self.axes is None:
            transpose_axis[-2], transpose_axis[-1] = \
                transpose_axis[-1], transpose_axis[-2]
        else:
            transpose_axis[self.axes[0]], transpose_axis[self.axes[1]] = \
                self.axes[1], self.axes[0]
        return array_api.transpose(a, transpose_axis)
        # raise NotImplementedError()
        ### END YOUR SOLUTION

    def gradient(self, out_grad, node):
        ### BEGIN YOUR SOLUTION

        return (transpose(out_grad, axes=self.axes), )

        # raise NotImplementedError()
        ### END YOUR SOLUTION


def transpose(a, axes=None):
    return Transpose(axes)(a)


class Reshape(TensorOp):
    def __init__(self, shape):
        self.shape = shape

    def compute(self, a):
        ### BEGIN YOUR SOLUTION
        return array_api.reshape(a.compact(), self.shape)
        # raise NotImplementedError()
        ### END YOUR SOLUTION

    def gradient(self, out_grad, node):
        ### BEGIN YOUR SOLUTION
        return (out_grad.reshape(node.inputs[0].shape), )
        # raise NotImplementedError()
        ### END YOUR SOLUTION


def reshape(a, shape):
    return Reshape(shape)(a)


class BroadcastTo(TensorOp):
    def __init__(self, shape):
        self.shape = shape

    def compute(self, a):
        ### BEGIN YOUR SOLUTION
        
        return array_api.broadcast_to(a, self.shape)
        # raise NotImplementedError()
        ### END YOUR SOLUTION

    def gradient(self, out_grad, node):
        ### BEGIN YOUR SOLUTION
        in_shape = node.inputs[0].shape
        out_shape = self.shape
        # breakpoint()
        grad = summation(out_grad, axes=tuple(range(len(out_shape)-len(in_shape))))
        sum_axis = []
        for i in range(len(in_shape)):
            d1, d2 = in_shape[i], out_shape[i]
            if d1 != d2 and d1 == 1:
                sum_axis.append(i)
        grad = summation(grad, axes=tuple(sum_axis))
        grad = reshape(grad, in_shape)
        assert grad.shape == in_shape, f"{grad.shape} {in_shape}"
        return (grad, )
        # raise NotImplementedError()
        ### END YOUR SOLUTION


def broadcast_to(a, shape):
    return BroadcastTo(shape)(a)


class Summation(TensorOp):
    def __init__(self, axes: Optional[tuple] = None):
        self.axes = axes

    def compute(self, a):
        ### BEGIN YOUR SOLUTION
        return array_api.sum(a, axis=self.axes)
        # return 
        # raise NotImplementedError()
        ### END YOUR SOLUTION

    def gradient(self, out_grad, node):
        ### BEGIN YOUR SOLUTION
        in_shape = node.inputs[0].shape
        if self.axes is not None:
            out_grad = array_api.expand_dims(out_grad.cached_data, self.axes)
        grad = broadcast_to(Tensor(out_grad), in_shape)
        return (Tensor(grad) ,)
        # raise NotImplementedError()
        ### END YOUR SOLUTION


def summation(a, axes=None):
    return Summation(axes)(a)


class MatMul(TensorOp):
    def compute(self, a, b):
        ### BEGIN YOUR SOLUTION
        return array_api.matmul(a, b)
        # raise NotImplementedError()
        ### END YOUR SOLUTION

    def gradient(self, out_grad, node):
        ### BEGIN YOUR SOLUTION
        mat_1, mat_2 = node.inputs[0], node.inputs[1]
        # breakpoint()

        grad_1 = matmul(out_grad, transpose(mat_2))
        grad_2 = matmul(transpose(mat_1), out_grad)
        
        # breakpoint()
        if grad_2.shape != mat_2.shape:
            grad_2 = summation(grad_2, axes=tuple(range(len(grad_2.shape)-len(mat_2.shape))))
        if grad_1.shape != mat_1.shape:
            grad_1 = summation(grad_1, axes=tuple(range(len(grad_1.shape)-len(mat_1.shape))))

        return grad_1, grad_2
        # raise NotImplementedError()
        ### END YOUR SOLUTION


def matmul(a, b):
    return MatMul()(a, b)


class Negate(TensorOp):
    def compute(self, a):
        ### BEGIN YOUR SOLUTION
        return -1 * a
        # raise NotImplementedError()
        ### END YOUR SOLUTION

    def gradient(self, out_grad, node):
        ### BEGIN YOUR SOLUTION
        return (-1 * out_grad, )
        # raise NotImplementedError()
        ### END YOUR SOLUTION


def negate(a):
    return Negate()(a)


class Log(TensorOp):
    def compute(self, a):
        ### BEGIN YOUR SOLUTION
        return array_api.log(a)
        # raise NotImplementedError()
        ### END YOUR SOLUTION

    def gradient(self, out_grad, node):
        ### BEGIN YOUR SOLUTION
        return (out_grad * (Tensor(1) / node.inputs[0]), )
        # raise NotImplementedError()
        ### END YOUR SOLUTION


def log(a):
    return Log()(a)


class Exp(TensorOp):
    def compute(self, a):
        ### BEGIN YOUR SOLUTION
        return array_api.exp(a)
        # raise NotImplementedError()
        ### END YOUR SOLUTION

    def gradient(self, out_grad, node):
        ### BEGIN YOUR SOLUTION
        return (out_grad * exp(node.inputs[0]), )
        # raise NotImplementedError()
        ### END YOUR SOLUTION


def exp(a):
    return Exp()(a)


class ReLU(TensorOp):
    def compute(self, a):
        ### BEGIN YOUR SOLUTION
        # breakpoint()
        return array_api.maximum(a, 0)
        # return a * (a>=0)
        # raise NotImplementedError()
        ### END YOUR SOLUTION

    def gradient(self, out_grad, node):
        ### BEGIN YOUR SOLUTION
        return out_grad * (node.inputs[0].cached_data>=0), 
        # raise NotImplementedError()
        ### END YOUR SOLUTION


def relu(a):
    return ReLU()(a)
