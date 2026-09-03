import fastf1
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }

    h1, h2, h3 {
        color: #FFFFFF;
    }

    p, label {
        color: #B8BCC5;
    }
</style>
""", unsafe_allow_html=True)

fastf1.Cache.enable_cache("./cache")

schedule = fastf1.get_event_schedule(2025, include_testing=False)
locations = schedule['Location']

title_col, logo_col = st.columns([4, 1])

with title_col:
    st.title("Mercedes 2025 Qualifying Performance")
    st.caption("A data-driven comparison of Mercedes qualifying performance across the 2025 Formula 1 season using FastF1, pandas, NumPy and Streamlit.")
    sp1 , sp2 = st.columns([5,1])
    with sp1:
        selectedGp = st.selectbox('Selecte the Grand Prix', locations)
    with sp2:
        st.image("assets/f1.png", width=70)

    st.subheader(f"Kimi Antonelli vs George Russell — {selectedGp}")

with logo_col:
        st.image("assets/merc.png", width=180)
        

#st.title("Mercedes 2025 Qualifying Performance")


#st.subheader(f"Kimi Antonelli vs George Russell — {selectedGp}")
session = fastf1.get_session(2025, selectedGp, 'Q')
with st.spinner("BOX BOX BOX.."):
    session.load()

j = session.laps


session.laps.to_csv("laps.csv", index=False)

antLaps = j.pick_driver('ANT')
rusLaps = j.pick_driver('RUS')

antClean = antLaps[(antLaps['IsAccurate'] == True) & (antLaps['Deleted'] == False)]
rusClean = rusLaps[(rusLaps['IsAccurate'] == True) & (rusLaps['Deleted'] == False)]


antStd = antClean.groupby('Compound')['LapTime'].std();
rusStd = rusClean.groupby('Compound')['LapTime'].std();

antBest = antClean['LapTime'].min()
rusBest = rusClean['LapTime'].min()

antPace = antClean[antClean['LapTime'] <= (antBest * 1.02)]
rusPace = rusClean[rusClean['LapTime'] <= (rusBest * 1.02)]

antBestPace = antPace['LapTime'].min()###.dt.total_seconds()
rusBestPace = rusPace['LapTime'].min()###.dt.total_seconds()

avgDiff = antPace['LapTime'].mean() - rusPace['LapTime'].mean()

bestInterval = antBestPace - rusBestPace 

antConsistency = antPace['LapTime'].std().total_seconds()
rusConsistency = rusPace['LapTime'].std().total_seconds()

consistencyDiff = antConsistency - rusConsistency

a = antPace[['Sector1Time', 'Sector2Time', 'Sector3Time']].std().dt.total_seconds()
b = rusPace[['Sector1Time', 'Sector2Time', 'Sector3Time']].std().dt.total_seconds()

concatedSDsector = pd.concat([a,b], axis=1, keys=['ANT', 'RUS'])

antSecAvg = antPace[['Sector1Time', 'Sector2Time', 'Sector3Time']].mean().dt.total_seconds()
rusSecAvg = rusPace[['Sector1Time', 'Sector2Time', 'Sector3Time']].mean().dt.total_seconds()


antTyreAvg = antPace.groupby('Compound')['LapTime'].mean().dt.total_seconds()
rusTyreAvg = rusPace.groupby('Compound')['LapTime'].mean().dt.total_seconds()

diffText = "slower than Russell"

if bestInterval.total_seconds() < 0:
    diffText = "faster than Russell"

avgDeltaColor = "inverse"

if avgDiff.total_seconds() < 0:
    avgDeltaColor = "normal"

bestDeltaColor = "inverse"

if bestInterval.total_seconds() < 0:
    bestDeltaColor = "normal"

col1 , col2 = st.columns(2)

with col1:
    col11 , col12 = st.columns([1.25,1])
    with col11:
        st.metric("Antonelli's best (s)",f'{antBestPace.total_seconds():.3f}', delta=f"{abs(bestInterval.total_seconds()):.3f} s {diffText}", delta_color=bestDeltaColor)
    with col12:
        st.image("assets/kimi.png", width=70)
with col2:
    col21 , col22 = st.columns([1.25,1])
    with col21:
        st.metric("Russell's best (s)", f'{rusBestPace.total_seconds():.3f}')
    with col22:
        st.image("assets/rus.png", width=70)


if consistencyDiff < 0:
    consistencyInsight = f"ANT was more consistent by {abs(consistencyDiff):.3f}s"
else:
    consistencyInsight = f"Russell was more consistent by {consistencyDiff:.3f}s"



avgDiffText = "slower than Russell"

if avgDiff.total_seconds() < 0:
    avgDiffText = "faster than Russell"


col3 , col4 = st.columns(2)

with col3:
    st.metric("Interval between both the drivers (s)", f'{bestInterval.total_seconds():.3f}')
with col4:
    st.metric("Avg difference between both the drivers in seconds (s)", f"{avgDiff.total_seconds():.3f}",delta=f"{abs(avgDiff.total_seconds()):.3f} s {avgDiffText}", delta_color=avgDeltaColor)


col5, col6 = st.columns(2)

with col5:
    st.metric("Antonelli's pace consistency (s)", f"{antConsistency:.3f}")

with col6:
    st.metric("Russell's pace consistency (s)", f"{rusConsistency:.3f}")



sectorDiff = antSecAvg - rusSecAvg
biggestSec = sectorDiff.idxmax()
SecGap = sectorDiff.max()
biggestSecNum = biggestSec.replace("Time","").replace("Sector"," ")


biggestSector = sectorDiff.abs().idxmax()
biggestSecGap = sectorDiff[biggestSector]

if biggestSecGap > 0:
    sectorInsight = f"ANT lost {biggestSecGap:.3f}s in Sector {biggestSecNum}"
else:
    sectorInsight = f"ANT gained {abs(biggestSecGap):.3f}s in Sector {biggestSecNum}"

concSecAvg = pd.concat([antSecAvg, rusSecAvg], axis=1, keys=['ANT', 'RUS'])


tyreDiff = antTyreAvg - rusTyreAvg
compoundType = tyreDiff.abs().idxmax()
compoundTypeVal = tyreDiff[compoundType]

if compoundTypeVal > 0:
    tyreInsight = f"ANT lost {compoundTypeVal:.3f}s on {compoundType}"
else:
    tyreInsight = f"ANT gained {abs(compoundTypeVal):.3f}s on {compoundType}"

tyreAdvConcat = pd.concat([antTyreAvg, rusTyreAvg], axis=1, keys=['ANT', 'RUS'])

print(f'{tyreAdvConcat}')


graph_col1, graph_col2 = st.columns(2)

with graph_col1:
    ##----------------
    ##Graph 1 — Representative Lap Pace

    plt.figure()

    antPaceSecs = antPace['LapTime'].dt.total_seconds()
    rusPaceSecs = rusPace['LapTime'].dt.total_seconds()

    st.caption("Note:the lowest point denotes the fastest lap")
    plt.plot(antPace['LapNumber'], antPaceSecs, label='ANT', color='#000000')
    plt.plot(rusPace['LapNumber'], rusPaceSecs, label = 'RUS', color='#4FAFA9')

    plt.xlabel('Lap Number')
    plt.ylabel('Time in seconds')
    plt.legend()
    plt.title('Antonelli vs Russell: Representative Lap Comparison')

    # plt.figtext(0.5, 0.01, 'Note:the lowest point denotes the fastest lap',ha='center')
    plt.tight_layout()

    #plt.show()

    st.pyplot(plt)
    

with graph_col2:
    ##----------------
    ##Graph 2 - Sector Comparison

    plt.figure()
    x = np.arange(3)
    width = 0.35
    st.caption(sectorInsight)
    plt.bar(x - width/2 , concSecAvg['ANT'], width, label='ANT', color='#000000')
    plt.bar(x + width/2 , concSecAvg['RUS'], width, label='RUS', color='#4FAFA9')


    plt.title('Kimi vs Russell: Sector Comparison')
    plt.xticks(x, ['Sector 1','Sector 2','Sector 3'])
    plt.yticks(range(0,50 ,2))
    plt.xlabel('Sectors')
    plt.ylabel('Time in seconds')
    plt.legend()

    #plt.show()
    st.pyplot(plt)


graph_col3, graph_col4 = st.columns(2)

with graph_col3:
    
    ##-----------------
    ##Graph 3 - Compound Comparison
    plt.figure()
    y = np.arange(2)

    width = 0.30
    st.caption(tyreInsight)
    plt.bar(y - width/2, tyreAdvConcat['ANT'], width, label = 'ANT', color='#000000')
    plt.bar(y + width/2, tyreAdvConcat['RUS'], width, label = 'RUS', color='#4FAFA9')

    plt.xticks(y, ['MEDIUM', 'SOFT'])
    plt.title('Kimi vs Russell: Tyre Compound Comparison')
    plt.yticks(range(1, 130, 10))
    plt.xlabel('Compound')
    plt.ylabel('Time in seconds')
    plt.legend()

    #plt.show()
    st.pyplot(plt)


with graph_col4:

    ## Graph 4 - Sector Consistency

    plt.figure()
    x = np.arange(3)
    width = 0.35
    st.caption(consistencyInsight)
    plt.bar(x - width/2, concatedSDsector['ANT'], width, label='ANT',color='#000000')
    plt.bar(x + width/2, concatedSDsector['RUS'], width, label='RUS', color='#4FAFA9')

    plt.xticks(x, ['Sector 1', 'Sector 2', 'Sector 3'])
    plt.xlabel('Sectors')
    plt.ylabel('Standard Deviation (seconds)')
    plt.title('Kimi vs Russell: Sector Consistency')
    plt.legend()

    #plt.show()
    st.pyplot(plt)



with st.expander("About this analysis"):
    st.write("Only accurate and non-deleted qualifying laps are considered.")
    st.write("Representative laps are defined as laps within 2% of each driver's best clean lap.")
    st.write("Lower lap time indicates better pace, while lower standard deviation indicates greater consistency.")




