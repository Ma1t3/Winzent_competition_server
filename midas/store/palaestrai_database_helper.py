import palaestrai.store.database_model as dbm
import sqlalchemy as sa
from palaestrai.core import RuntimeConfig


class PalaestraiDatabaseHelper:
    """Helper functions for the palaestrai database"""

    def __init__(self, uid):
        self._db_session = None
        self.store_uri = RuntimeConfig().store_uri
        self.uid = str(uid)

    def get_experiment_rating_function(self):
        rating_function = "pgasc.midas.analyze.rating_functions.default_rating_function.DefaultRatingFunction"
        try:
            # get experiment run definition from palaestrai db
            query = self._dbh().query(dbm.ExperimentRun.document)
            query = query.filter(dbm.ExperimentRun.uid == self.uid)

            # get schedule_config from palaestrai json
            schedule_config = query[0][0]["schedule_config"][0]
            phase_name = list(schedule_config.keys())[0]
            # get enviroment_params from palaestrai json
            enviroment_params = schedule_config[phase_name]["environments"][0][
                "environment"
            ]["params"]
            rating_function = enviroment_params["rating_function"]

            self.disable()
        except Exception:
            self.disable()

        return rating_function

    def _dbh(self):
        # use a session for Database safe
        if self._db_session is None:
            self._db_engine = sa.create_engine(self.store_uri)
            self._db_session_maker = sa.orm.sessionmaker()
            self._db_session_maker.configure(bind=self._db_engine)
            try:
                self._db_session = self._db_session_maker()
            except Exception:
                self.disable()
                raise
        return self._db_session

    def disable(self):
        # close open Database session
        if self._db_session:
            self._db_session.close()
        self._db_session = None
