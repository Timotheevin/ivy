# global
import sys
import numpy as np

from hypothesis import strategies as st

# local
import ivy
import ivy_tests.test_ivy.helpers as helpers
from ivy_tests.test_ivy.helpers import assert_all_close, handle_frontend_test
from ivy_tests.test_ivy.test_functional.test_core.test_linalg import (
    _get_dtype_and_matrix,
    _matrix_rank_helper,
)


# svd
@handle_frontend_test(
    fn_tree="jax.numpy.linalg.svd",
    dtype_and_x=helpers.dtype_and_values(
        available_dtypes=helpers.get_dtypes("float"),
        min_value=0,
        max_value=10,
        shape=helpers.ints(min_value=2, max_value=5).map(lambda x: tuple([x, x])),
    ).filter(
        lambda x: "float16" not in x[0]
        and "bfloat16" not in x[0]
        and np.linalg.cond(x[1][0]) < 1 / sys.float_info.epsilon
        and np.linalg.det(np.asarray(x[1][0])) != 0
    ),
    full_matrices=st.booleans(),
    compute_uv=st.booleans(),
)
def test_jax_numpy_svd(
    *,
    dtype_and_x,
    full_matrices,
    compute_uv,
    as_variable,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, x = dtype_and_x
    x = np.asarray(x[0], dtype=dtype[0])
    # make symmetric positive-definite beforehand
    x = np.matmul(x.T, x) + np.identity(x.shape[0]) * 1e-3

    ret, frontend_ret = helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        test_values=False,
        x=x,
        full_matrices=full_matrices,
        compute_uv=compute_uv,
    )

    if compute_uv:
        ret = [ivy.to_numpy(x) for x in ret]
        frontend_ret = [np.asarray(x) for x in frontend_ret]

        u, s, vh = ret
        frontend_u, frontend_s, frontend_vh = frontend_ret

        assert_all_close(
            ret_np=u @ np.diag(s) @ vh,
            ret_from_gt_np=frontend_u @ np.diag(frontend_s) @ frontend_vh,
            rtol=1e-2,
            atol=1e-2,
            ground_truth_backend=frontend,
        )
    else:
        assert_all_close(
            ret_np=ivy.to_numpy(ret),
            ret_from_gt_np=np.asarray(frontend_ret[0]),
            rtol=1e-2,
            atol=1e-2,
            ground_truth_backend=frontend,
        )


# det
@handle_frontend_test(
    fn_tree="jax.numpy.linalg.det",
    dtype_and_x=_get_dtype_and_matrix(),
)
def test_jax_numpy_det(
    *,
    dtype_and_x,
    as_variable,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, x = dtype_and_x
    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        rtol=1e-04,
        atol=1e-04,
        a=x[0],
    )


# eig
@handle_frontend_test(
    fn_tree="jax.numpy.linalg.eig",
    dtype_and_x=_get_dtype_and_matrix(),
)
def test_jax_numpy_eig(
    *,
    dtype_and_x,
    as_variable,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, x = dtype_and_x
    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        rtol=1e-04,
        atol=1e-04,
        a=x[0],
    )


# eigh
@handle_frontend_test(
    fn_tree="jax.numpy.linalg.eigh",
    dtype_and_x=helpers.dtype_and_values(
        available_dtypes=helpers.get_dtypes("float"),
        min_value=0,
        max_value=10,
        shape=helpers.ints(min_value=2, max_value=5).map(lambda x: tuple([x, x])),
    ).filter(
        lambda x: "float16" not in x[0]
        and "bfloat16" not in x[0]
        and np.linalg.cond(x[1][0]) < 1 / sys.float_info.epsilon
        and np.linalg.det(np.asarray(x[1][0])) != 0
    ),
    UPLO=st.sampled_from(("L", "U")),
    symmetrize_input=st.booleans(),
)
def test_jax_numpy_eigh(
    *,
    dtype_and_x,
    UPLO,
    symmetrize_input,
    as_variable,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, x = dtype_and_x
    x = np.array(x[0], dtype=dtype[0])
    # make symmetric positive-definite beforehand
    x = np.matmul(x.T, x) + np.identity(x.shape[0]) * 1e-3

    ret, frontend_ret = helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        test_values=False,
        a=x,
        UPLO=UPLO,
        symmetrize_input=symmetrize_input,
    )
    ret = [ivy.to_numpy(x) for x in ret]
    frontend_ret = [np.asarray(x) for x in frontend_ret]

    L, Q = ret
    frontend_L, frontend_Q = frontend_ret

    assert_all_close(
        ret_np=Q @ np.diag(L) @ Q.T,
        ret_from_gt_np=frontend_Q @ np.diag(frontend_L) @ frontend_Q.T,
        atol=1e-02,
    )


# inv
@handle_frontend_test(
    fn_tree="jax.numpy.linalg.inv",
    dtype_and_x=helpers.dtype_and_values(
        available_dtypes=helpers.get_dtypes("float"),
        min_value=-100,
        max_value=100,
        shape=helpers.ints(min_value=1, max_value=10).map(lambda x: tuple([x, x])),
    ).filter(
        lambda x: "float16" not in x[0]
        and "bfloat16" not in x[0]
        and np.linalg.cond(x[1][0]) < 1 / sys.float_info.epsilon
        and np.linalg.det(np.asarray(x[1][0])) != 0
    ),
)
def test_jax_numpy_inv(
    *,
    dtype_and_x,
    as_variable,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, x = dtype_and_x
    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        rtol=1e-01,
        atol=1e-01,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        a=x[0],
    )


# eigvalsh
@handle_frontend_test(
    fn_tree="jax.numpy.linalg.eigvalsh",
    dtype_and_x=helpers.dtype_and_values(
        available_dtypes=helpers.get_dtypes("float"),
        min_value=0,
        max_value=10,
        shape=helpers.ints(min_value=2, max_value=5).map(lambda x: tuple([x, x])),
    ).filter(
        lambda x: "float16" not in x[0]
        and "bfloat16" not in x[0]
        and np.linalg.cond(x[1][0]) < 1 / sys.float_info.epsilon
        and np.linalg.det(np.asarray(x[1][0])) != 0
    ),
    UPLO=st.sampled_from(("L", "U")),
)
def test_jax_numpy_eigvalsh(
    *,
    dtype_and_x,
    UPLO,
    as_variable,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, x = dtype_and_x
    x = np.asarray(x[0], dtype=dtype[0])
    # make symmetric positive-definite beforehand
    x = np.matmul(x.T, x) + np.identity(x.shape[0]) * 1e-3
    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        rtol=1e-02,
        atol=1e-02,
        a=x,
        UPLO=UPLO,
    )


# qr
@handle_frontend_test(
    fn_tree="jax.numpy.linalg.qr",
    dtype_and_x=helpers.dtype_and_values(
        available_dtypes=helpers.get_dtypes("float"),
        min_num_dims=3,
        max_num_dims=5,
        min_dim_size=2,
        max_dim_size=5,
        min_value=2,
        max_value=5,
    ),
    mode=st.sampled_from(("reduced", "complete")),
)
def test_jax_numpy_qr(
    *,
    dtype_and_x,
    mode,
    as_variable,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, x = dtype_and_x
    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        rtol=1e-01,
        atol=1e-01,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        a=np.asarray(x[0], dtype[0]),
        mode=mode,
    )


# eigvals
@handle_frontend_test(
    fn_tree="jax.numpy.linalg.eigvals",
    dtype_and_x=helpers.dtype_and_values(
        available_dtypes=helpers.get_dtypes("float"),
        min_value=0,
        max_value=10,
        shape=helpers.ints(min_value=2, max_value=5).map(lambda x: tuple([x, x])),
    ).filter(
        lambda x: "float16" not in x[0]
        and "bfloat16" not in x[0]
        and np.linalg.cond(x[1][0]) < 1 / sys.float_info.epsilon
        and np.linalg.det(np.asarray(x[1][0])) != 0
    ),
)
def test_jax_numpy_eigvals(
    *,
    dtype_and_x,
    as_variable,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, x = dtype_and_x
    x = np.array(x[0], dtype=dtype[0])
    # make symmetric positive-definite beforehand
    x = np.matmul(x.T, x) + np.identity(x.shape[0]) * 1e-3

    ret, frontend_ret = helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        test_values=False,
        a=x,
    )


# cholesky
@handle_frontend_test(
    fn_tree="jax.numpy.linalg.cholesky",
    dtype_and_x=helpers.dtype_and_values(
        available_dtypes=helpers.get_dtypes("float"),
        min_value=0,
        max_value=10,
        shape=helpers.ints(min_value=2, max_value=5).map(lambda x: tuple([x, x])),
    ).filter(
        lambda x: "float16" not in x[0]
        and "bfloat16" not in x[0]
        and np.linalg.cond(x[1][0]) < 1 / sys.float_info.epsilon
        and np.linalg.det(x[1][0]) != 0
    ),
)
def test_jax_numpy_cholesky(
    *,
    dtype_and_x,
    as_variable,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, x = dtype_and_x
    x = np.asarray(x[0], dtype=dtype[0])
    # make symmetric positive-definite
    x = np.matmul(x.T, x) + np.identity(x.shape[0]) * 1e-3

    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        rtol=1e-02,
        a=x,
    )


# slogdet
@handle_frontend_test(
    fn_tree="jax.numpy.linalg.slogdet",
    dtype_and_x=helpers.dtype_and_values(
        available_dtypes=helpers.get_dtypes("float"),
        max_value=100,
        min_value=-100,
        shape=st.tuples(
            st.shared(st.integers(1, 5), key="sq"),
            st.shared(st.integers(1, 5), key="sq"),
        ),
        num_arrays=1,
    ),
)
def test_jax_slogdet(
    *,
    dtype_and_x,
    as_variable,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    input_dtype, x = dtype_and_x
    helpers.test_frontend_function(
        input_dtypes=input_dtype,
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        a=x[0],
    )


# matrix_rank
@handle_frontend_test(
    fn_tree="jax.numpy.linalg.matrix_rank",
    dtype_and_x=_matrix_rank_helper(),
)
def test_jax_numpy_matrix_rank(
    *,
    dtype_and_x,
    as_variable,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, x = dtype_and_x
    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        M=x[0],
    )


# solve
@handle_frontend_test(
    fn_tree="jax.numpy.linalg.solve",
    dtype_and_data=helpers.dtype_and_values(
        available_dtypes=helpers.get_dtypes("float"),
        min_value=0,
        max_value=10,
        shape=helpers.ints(min_value=2, max_value=5).map(lambda x: tuple([x, x + 1])),
    ).filter(
        lambda x: "float16" not in x[0]
        and "bfloat16" not in x[0]
        and np.linalg.cond(x[1][0][:, :-1]) < 1 / sys.float_info.epsilon
        and np.linalg.det(x[1][0][:, :-1]) != 0
        and np.linalg.cond(x[1][0][:, -1].reshape(-1, 1)) < 1 / sys.float_info.epsilon
    ),
)
def test_jax_numpy_solve(
    *,
    dtype_and_data,
    as_variable,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    input_dtype, data = dtype_and_data
    a = data[0][:, :-1]
    b = data[0][:, -1].reshape(-1, 1)
    helpers.test_frontend_function(
        input_dtypes=[input_dtype[0], input_dtype[0]],
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        a=np.asarray(a, dtype=input_dtype[0]),
        b=np.asarray(b, dtype=input_dtype[0]),
        rtol=1e-01,
        atol=1e-01,
    )


@st.composite
def norm_helper(draw):
    dtype, x = draw(helpers.dtype_and_values(
        shape=st.shared(helpers.get_shape(min_num_dims=1), key="shape"),
        available_dtypes=helpers.get_dtypes("valid"),
        min_num_dims=1,
        safety_factor_scale="log",
        large_abs_safety_factor=2,
    ))
    axis = draw(helpers.get_axis(
        shape=st.shared(helpers.get_shape(min_num_dims=1), key="shape"),
    ))
    if type(axis) in [tuple, list]:
        if len(axis) == 2:
            ord_param = draw(
                st.sampled_from(["fro", "nuc", 1, 2, -1, -2, np.inf, -np.inf])
            )
        else:
            axis = axis[0]
            ord_param = draw(st.sampled_from([0, 1, 2, -1, -2, np.inf, -np.inf]))
    else:
        ord_param = draw(st.sampled_from([0, 1, 2, -1, -2, np.inf, -np.inf]))
    keepdims = draw(st.booleans())
    return dtype, x, ord_param, axis, keepdims


# norm
@handle_frontend_test(
    fn_tree="jax.numpy.linalg.norm",
    params=norm_helper().filter(lambda s: "bfloat16" not in s[0] or "bool" not in s[0]),
)
def test_jax_norm(
    *,
    params,
    as_variable,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, x, ord_param, axis, keepdims = params

    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        x=x[0],
        ord=ord_param,
        axis=axis,
        keepdims=keepdims,
    )


# matrix_power
@handle_frontend_test(
    fn_tree="jax.numpy.linalg.matrix_power",
    dtype_and_x=helpers.dtype_and_values(
        available_dtypes=helpers.get_dtypes("float"),
        min_value=-100,
        max_value=100,
        shape=helpers.ints(min_value=1, max_value=10).map(lambda x: tuple([x, x])),
    ).filter(
        lambda x: "float16" not in x[0]
        and "bfloat16" not in x[0]
        and np.linalg.cond(x[1][0]) < 1 / sys.float_info.epsilon
        and np.linalg.det(np.asarray(x[1][0])) != 0
    ),
    n=helpers.ints(min_value=1, max_value=8),
)
def test_jax_numpy_matrix_power(
    *,
    dtype_and_x,
    n,
    as_variable,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, x = dtype_and_x
    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        rtol=1e-01,
        atol=1e-01,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        a=np.asarray(x[0], dtype=dtype[0]),
        n=n,
    )


# tensorsolve
@st.composite
def _get_solve_matrices(draw):
    # batch_shape, random_size, shared

    # float16 causes a crash when filtering out matrices
    # for which `np.linalg.cond` is large.
    input_dtype_strategy = st.shared(
        st.sampled_from(draw(helpers.get_dtypes("float"))).filter(
            lambda x: "float16" not in x
        ),
        key="shared_dtype",
    )
    input_dtype = draw(input_dtype_strategy)

    first_size = draw(helpers.ints(min_value=2, max_value=3))

    random_size = draw(
        st.shared(helpers.ints(min_value=2, max_value=3), key="random_size")
    )

    first_matrix = draw(
        helpers.array_values(
            dtype=input_dtype,
            shape=(random_size, first_size, first_size, random_size),
            min_value=1.2,
            max_value=5,
        ).filter(lambda x: (np.linalg.cond(x) < 1 / sys.float_info.epsilon).all())
    )
    second_matrix = draw(
        helpers.array_values(
            dtype=input_dtype,
            shape=(random_size, first_size),
            min_value=1.2,
            max_value=3,
        ).filter(lambda x: (np.linalg.cond(x) < 1 / sys.float_info.epsilon).all())
    )

    return input_dtype, first_matrix, second_matrix


@handle_frontend_test(
    fn_tree="jax.numpy.linalg.tensorsolve",
    a_and_b=_get_solve_matrices(),
)
def test_jax_numpy_tensorsolve(
    *,
    a_and_b,
    as_variable,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    input_dtype, x, y = a_and_b
    helpers.test_frontend_function(
        input_dtypes=[input_dtype],
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        a=x,
        b=y,
    )


# pinv
@handle_frontend_test(
    fn_tree="jax.numpy.linalg.pinv",
    dtype_and_x=helpers.dtype_and_values(
        available_dtypes=helpers.get_dtypes("float"),
        min_num_dims=2,
        max_num_dims=5,
        min_dim_size=2,
        max_dim_size=5,
        large_abs_safety_factor=32,
        small_abs_safety_factor=32,
        safety_factor_scale="log",
    ),
)
def test_jax_numpy_pinv(
    dtype_and_x, as_variable, native_array, num_positional_args, frontend, fn_tree
):
    dtype, x = dtype_and_x
    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        a=x[0],
    )
