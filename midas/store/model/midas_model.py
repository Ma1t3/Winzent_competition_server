import sqlalchemy as sa

from pgasc.midas.store.model.meta_base import Base


class PPStaticGeneratorMeta(Base):
    __tablename__ = "pp_static_generator_meta"

    experiment_id = sa.Column(sa.INTEGER, primary_key=True)
    pp_index = sa.Column(sa.INTEGER, primary_key=True)

    name = sa.Column(sa.String)
    x = sa.Column(sa.Float)
    y = sa.Column(sa.Float)

    def __str__(self):
        return (
            f'<PPStaticGeneratorMeta(experiment_id={self.experiment_id}, pp_index="'
            f'{self.pp_index}", name="{self.name}", x="{self.x}", y="{self.y}">'
        )


class PPStaticGenerator(Base):
    __tablename__ = "pp_static_generator"

    id = sa.Column(sa.INTEGER, primary_key=True, unique=True, index=True)
    experiment_id = sa.Column(sa.INTEGER)
    pp_index = sa.Column(sa.Integer)

    time = sa.Column(sa.DateTime)
    p_mw = sa.Column(sa.Float)
    q_mvar = sa.Column(sa.Float)
    scaling = sa.Column(sa.Float)
    in_service = sa.Column(sa.Boolean)

    sa.ForeignKeyConstraint(
        ["experiment_id", "pp_index"],
        [
            "pp_static_generator_meta.experiment_id",
            "pp_static_generator_meta.pp_index",
        ],
    )

    def __str__(self):
        return (
            f'<PPStaticGenerator(experiment_id={self.experiment_id}, pp_index="'
            f'{self.pp_index}", time={self.time}, p_mw={self.p_mw}, q_mvar={self.q_mvar},'
            f"scaling={self.scaling}, in_service={self.in_service}>"
        )


class PPLoadMeta(Base):
    __tablename__ = "pp_load_meta"

    experiment_id = sa.Column(sa.INTEGER, primary_key=True)
    pp_index = sa.Column(sa.INTEGER, primary_key=True)

    name = sa.Column(sa.String)
    x = sa.Column(sa.Float)
    y = sa.Column(sa.Float)

    def __str__(self):
        return (
            f'<PPLoadMeta(experiment_id={self.experiment_id}, pp_index="'
            f'{self.pp_index}", name="{self.name}", x="{self.x}", y="{self.y}">'
        )


class PPLoad(Base):
    __tablename__ = "pp_load"

    id = sa.Column(sa.INTEGER, primary_key=True, unique=True, index=True)
    experiment_id = sa.Column(sa.INTEGER)
    pp_index = sa.Column(sa.Integer)

    time = sa.Column(sa.DateTime)
    p_mw = sa.Column(sa.Float)
    q_mvar = sa.Column(sa.Float)
    scaling = sa.Column(sa.Float)
    in_service = sa.Column(sa.Boolean)

    sa.ForeignKeyConstraint(
        ["experiment_id", "pp_index"],
        ["pp_load_meta.experiment_id", "pp_load_meta.pp_index"],
    )

    def __str__(self):
        return (
            f'<PPLoad(id={self.id}, experiment_id={self.experiment_id}, pp_index="'
            f'{self.pp_index}", time={self.time}, p_mw={self.p_mw}, q_mvar={self.q_mvar},'
            f"scaling={self.scaling}, in_service={self.in_service}>"
        )


class PPBusMeta(Base):
    __tablename__ = "pp_bus_meta"

    experiment_id = sa.Column(sa.INTEGER, primary_key=True)
    pp_index = sa.Column(sa.INTEGER, primary_key=True)

    name = sa.Column(sa.String)
    vn_kv = sa.Column(sa.Float)
    type = sa.Column(sa.String)
    zone = sa.Column(sa.String)

    def __str__(self):
        return (
            f'<PPBusMeta(pp_index="'
            f'{self.pp_index}", experiment_id={self.experiment_id}, name="{self.name}", vn_kv="{self.vn_kv}", type="{self.type}", zone="{self.zone}">'
        )


class PPBus(Base):
    __tablename__ = "pp_bus"

    id = sa.Column(sa.INTEGER, primary_key=True, unique=True, index=True)
    experiment_id = sa.Column(sa.INTEGER)
    pp_index = sa.Column(sa.INTEGER)

    time = sa.Column(sa.DateTime)
    vm_pu = sa.Column(sa.Float)
    va_degree = sa.Column(sa.Float)
    p_mw = sa.Column(sa.Float)
    q_mvar = sa.Column(sa.Float)
    in_service = sa.Column(sa.Boolean)

    sa.ForeignKeyConstraint(
        ["experiment_id", "pp_index"],
        ["pp_bus_meta.experiment_id", "pp_bus_meta.pp_index"],
    )

    def __str__(self):
        return (
            f'<PPBus(id={self.id}, experiment_id={self.experiment_id}, pp_index="'
            f'{self.pp_index}", time={self.time}, vm_pu={self.vm_pu}, va_degree={self.va_degree}, p_mw={self.p_mw}, '
            f"q_mvar={self.q_mvar},"
            f"in_service={self.in_service}>"
        )


class PPLineMeta(Base):
    __tablename__ = "pp_line_meta"

    experiment_id = sa.Column(sa.INTEGER, primary_key=True)
    pp_index = sa.Column(sa.INTEGER, primary_key=True)

    name = sa.Column(sa.String)
    std_type = sa.Column(sa.String)
    from_bus = sa.Column(sa.INTEGER)
    to_bus = sa.Column(sa.INTEGER)
    length_km = sa.Column(sa.Float)
    r_ohm_per_km = sa.Column(sa.Float)
    x_ohm_per_km = sa.Column(sa.Float)
    c_nf_per_km = sa.Column(sa.Float)
    g_us_per_km = sa.Column(sa.Float)
    max_i_ka = sa.Column(sa.Float)
    df = sa.Column(sa.Float)
    parallel = sa.Column(sa.INTEGER)
    type = sa.Column(sa.String)

    def __str__(self):
        return (
            f'<PPLineMeta(pp_index="'
            f'{self.pp_index}", name="{self.name}", std_type="{self.std_type}", from_bus="{self.from_bus}",'
            f'to_bus="{self.to_bus}", length_km="{self.length_km}", r_ohm_per_km="{self.r_ohm_per_km}", '
            f'x_ohm_per_km="{self.x_ohm_per_km}, c_nf_per_km="{self.c_nf_per_km}, g_us_per_km="{self.g_us_per_km}",'
            f'max_i_ka="{self.max_i_ka}, df="{self.df}, parallel="{self.parallel}, type="{self.type}> '
        )


class PPLine(Base):
    __tablename__ = "pp_line"

    id = sa.Column(sa.INTEGER, primary_key=True, unique=True, index=True)
    experiment_id = sa.Column(sa.INTEGER)
    pp_index = sa.Column(sa.INTEGER)

    time = sa.Column(sa.DateTime)
    p_from_mw = sa.Column(sa.Float)
    q_from_mvar = sa.Column(sa.Float)
    p_to_mw = sa.Column(sa.Float)
    q_to_mvar = sa.Column(sa.Float)
    pl_mw = sa.Column(sa.Float)
    ql_mvar = sa.Column(sa.Float)
    i_from_ka = sa.Column(sa.Float)
    i_to_ka = sa.Column(sa.Float)
    i_ka = sa.Column(sa.Float)
    vm_from_pu = sa.Column(sa.Float)
    va_from_degree = sa.Column(sa.Float)
    vm_to_pu = sa.Column(sa.Float)
    va_to_degree = sa.Column(sa.Float)
    loading_percent = sa.Column(sa.Float)
    in_service = sa.Column(sa.Boolean)

    sa.ForeignKeyConstraint(
        ["experiment_id", "pp_index"],
        ["pp_line_meta.experiment_id", "pp_line_meta.pp_index"],
    )

    def __str__(self):
        return (
            f'<PPLine(id={self.id}, pp_index="'
            f'{self.pp_index}", time="{self.time}", p_from_mw="{self.p_from_mw}", q_from_mvar="{self.q_from_mvar}",'
            f'p_to_mw="{self.p_to_mw}", q_to_mvar="{self.q_to_mvar}", pl_mw="{self.pl_mw}", '
            f'ql_mvar="{self.ql_mvar}, i_from_ka="{self.i_from_ka}, i_to_ka="{self.i_to_ka}",'
            f'i_ka="{self.i_ka}, vm_from_pu="{self.vm_from_pu}, va_from_degree="{self.va_from_degree},'
            f'vm_to_pu="{self.vm_to_pu},va_to_degree="{self.va_to_degree},'
            f'loading_percent="{self.loading_percent},in_service="{self.in_service}> '
        )


class PPTrafoMeta(Base):
    __tablename__ = "pp_trafo_meta"

    experiment_id = sa.Column(sa.INTEGER, primary_key=True)
    pp_index = sa.Column(sa.INTEGER, primary_key=True)

    name = sa.Column(sa.String)
    std_type = sa.Column(sa.String)
    hv_bus = sa.Column(sa.INTEGER)
    lv_bus = sa.Column(sa.INTEGER)
    sn_mva = sa.Column(sa.Float)
    vn_hv_kv = sa.Column(sa.Float)
    vn_lv_kv = sa.Column(sa.Float)
    vk_percent = sa.Column(sa.Float)
    vkr_percent = sa.Column(sa.Float)
    pfe_kw = sa.Column(sa.Float)
    i0_percent = sa.Column(sa.Float)
    shift_degree = sa.Column(sa.Float)
    # tap_side = sa.Column(sa.Float)
    # tap_neutral = sa.Column(sa.Float)
    # tap_min = sa.Column(sa.Float)
    # tap_max = sa.Column(sa.Float)
    tap_step_percent = sa.Column(sa.Float)
    tap_step_degree = sa.Column(sa.Float)
    tap_pos = sa.Column(sa.Float)
    tap_phase_shifter = sa.Column(sa.Boolean)

    # parallel = sa.Column(sa.INTEGER)
    # df = sa.Column(sa.Float)
    # pt_percent = sa.Column(sa.Float)
    # oltc = sa.Column(sa.Boolean)
    # tp_pos = sa.Column(sa.Float)

    def __str__(self):
        return (
            f'<PPTrafoMeta(pp_index="'
            f'{self.pp_index}", name="{self.name}", std_type="{self.std_type}", hv_bus="{self.hv_bus}",'
            f'lv_bus="{self.lv_bus}", sn_mva="{self.sn_mva}", vn_hv_kv="{self.vn_hv_kv}", '
            f'vn_lv_kv="{self.vn_lv_kv}, vk_percent="{self.vk_percent}, vkr_percent="{self.vkr_percent}",'
            f'pfe_kw="{self.pfe_kw}, i0_percent="{self.i0_percent}, shift_degree="{self.shift_degree}, '
            f'tap_step_percent="{self.tap_step_percent},'
            f'tap_step_degree="{self.tap_step_degree},tap_pos="{self.tap_pos},'
            f'tap_phase_shifter="{self.tap_phase_shifter}> '
        )


class PPTrafo(Base):
    __tablename__ = "pp_trafo"

    id = sa.Column(sa.INTEGER, primary_key=True, unique=True, index=True)
    experiment_id = sa.Column(sa.INTEGER)
    pp_index = sa.Column(sa.INTEGER)

    time = sa.Column(sa.DateTime)
    p_hv_mw = sa.Column(sa.Float)
    q_hv_mvar = sa.Column(sa.Float)
    p_lv_mw = sa.Column(sa.Float)
    q_lv_mvar = sa.Column(sa.Float)
    pl_mw = sa.Column(sa.Float)
    ql_mvar = sa.Column(sa.Float)
    i_hv_ka = sa.Column(sa.Float)
    i_lv_ka = sa.Column(sa.Float)
    vm_hv_pu = sa.Column(sa.Float)
    va_hv_degree = sa.Column(sa.Float)
    vm_lv_pu = sa.Column(sa.Float)
    va_lv_degree = sa.Column(sa.Float)
    loading_percent = sa.Column(sa.Float)
    in_service = sa.Column(sa.Boolean)

    sa.ForeignKeyConstraint(
        ["experiment_id", "pp_index"],
        ["pp_trafo_meta.experiment_id", "pp_trafo_meta.pp_index"],
    )

    def __str__(self):
        return (
            f'<PPTrafo(id={self.id}, pp_index="'
            f'{self.pp_index}", time="{self.time}", p_hv_mw="{self.p_hv_mw}", q_hv_mvar="{self.q_hv_mvar}",'
            f'p_lv_mw="{self.p_lv_mw}", q_lv_mvar="{self.q_lv_mvar}", pl_mw="{self.pl_mw}", '
            f'ql_mvar="{self.ql_mvar}, i_hv_ka="{self.i_hv_ka}, i_lv_ka="{self.i_lv_ka}",'
            f'vm_hv_pu="{self.vm_hv_pu}, va_hv_degree="{self.va_hv_degree}, vm_lv_pu="{self.vm_lv_pu},'
            f'va_lv_degree="{self.va_lv_degree},'
            f'loading_percent="{self.loading_percent},in_service="{self.in_service}> '
        )


class PPExtGridMeta(Base):
    __tablename__ = "pp_ext_grid_meta"

    experiment_id = sa.Column(sa.INTEGER, primary_key=True)
    pp_index = sa.Column(sa.INTEGER, primary_key=True)

    name = sa.Column(sa.String)
    bus = sa.Column(sa.INTEGER)

    def __str__(self):
        return (
            f'<PPExtGridMeta(experiment_id={self.experiment_id}, pp_index="'
            f'{self.pp_index}", name="{self.name}", bus="{self.bus}">'
        )


class PPExtGrid(Base):
    __tablename__ = "pp_ext_grid"

    id = sa.Column(sa.INTEGER, primary_key=True, unique=True, index=True)
    experiment_id = sa.Column(sa.INTEGER)
    pp_index = sa.Column(sa.Integer)

    time = sa.Column(sa.DateTime)
    p_mw = sa.Column(sa.Float)
    q_mvar = sa.Column(sa.Float)
    in_service = sa.Column(sa.Boolean)

    sa.ForeignKeyConstraint(
        ["experiment_id", "pp_index"],
        ["pp_ext_grid_meta.experiment_id", "pp_ext_grid_meta.pp_index"],
    )

    def __str__(self):
        return (
            f'<PPExtGrid(id={self.id}, experiment_id={self.experiment_id}, pp_index="'
            f'{self.pp_index}", time="{self.time}", p_mw="{self.p_mw}", '
            f'q_mvar={self.q_mvar}, in_service={self.in_service}>"'
        )


class Constraint(Base):
    __tablename__ = "constraint"

    id = sa.Column(sa.INTEGER, primary_key=True, unique=True, index=True)
    experiment_id = sa.Column(sa.INTEGER)
    pp_index = sa.Column(sa.INTEGER)

    type = sa.Column(sa.String)
    key = sa.Column(sa.String)
    time = sa.Column(sa.DateTime)

    def __str__(self):
        return (
            f'<Constraint(id={self.id}, experiment_id={self.experiment_id}, pp_index="'
            f'{self.pp_index}", type={self.type}, key={self.key}>'
        )


class ExperimentResult(Base):
    __tablename__ = "experiment_result"

    id = sa.Column(sa.INTEGER, primary_key=True, unique=True, index=True)
    experiment_id = sa.Column(sa.INTEGER)

    name = sa.Column(sa.String)
    value = sa.Column(sa.Float)
    unit = sa.Column(sa.String)

    def __str__(self):
        return (
            f'<ExperimentResult(experiment_id={self.experiment_id}, pp_index="'
            f'{self.pp_index}", name="{self.name}", value="{self.value}", unit="{self.unit}">'
        )


Model = Base
