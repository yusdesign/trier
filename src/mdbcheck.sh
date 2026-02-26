python -c "
import pandas as pd
from music_analyzer import MusicAnalyzer
a = MusicAnalyzer()
a.load_data()
print('✅ Timestamp column is datetime:', pd.api.types.is_datetime64_any_dtype(a.plays['timestamp']))
"
