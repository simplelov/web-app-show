import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
from pyecharts.charts import WordCloud, Bar, Pie, Line, Scatter, Radar, Funnel, HeatMap
from pyecharts import options as opts
from streamlit.components.v1 import html

# Streamlit界面设置
st.title('文章词频分析与词云展示')

# 用户输入文章URL
url = st.text_input('请输入文章URL')


# 抓取文本内容
def fetch_text_content(url):
    response = requests.get(url)
    response.encoding = 'utf-8'  # 设置编码为utf-8，避免乱码
    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.get_text()
    return text


# 分词并统计词频
def word_frequency(text):
    words = jieba.cut(text)
    freq = Counter(words)
    return freq  # 返回Counter对象


# 绘制词云
def draw_wordcloud(freq):
    if not freq:  # 检查freq是否为空
        return None
    wordcloud = WordCloud(init_opts=opts.InitOpts(width="1000px", height="600px"))
    wordcloud.add("", list(freq.items()), word_size_range=[20, 100])

    # 使用pyecharts的render方法生成图表的HTML内容
    return wordcloud.render_embed()


# 绘制图形
def draw_chart(chart_type, freq_dict):
    if not freq_dict:
        return None  # 如果freq_dict为空，不绘制图表

    if chart_type == '条形图':
        bar = Bar()
        bar.add_xaxis(list(freq_dict.keys()))
        bar.add_yaxis("词频", list(freq_dict.values()))
        bar.set_global_opts(title_opts=opts.TitleOpts(title=f"{chart_type}"))
        return bar.render_embed()

    elif chart_type == '饼图':
        pie = Pie()
        pie.add("", [list(z) for z in zip(list(freq_dict.keys()), list(freq_dict.values()))])
        pie.set_global_opts(
            title_opts=opts.TitleOpts(title=f"{chart_type}"),
            legend_opts=opts.LegendOpts(is_show=False)  # 隐藏图例，避免重叠
        )
        pie.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        return pie.render_embed()

    elif chart_type == '折线图':
        line = Line()
        line.add_xaxis(list(freq_dict.keys()))
        line.add_yaxis("词频", list(freq_dict.values()))
        line.set_global_opts(title_opts=opts.TitleOpts(title=f"{chart_type}"))
        return line.render_embed()

    elif chart_type == '散点图':
        scatter = Scatter()
        scatter.add_xaxis(list(freq_dict.keys()))
        scatter.add_yaxis("词频", list(freq_dict.values()))
        scatter.set_global_opts(title_opts=opts.TitleOpts(title=f"{chart_type}"))
        return scatter.render_embed()

    elif chart_type == '雷达图':
        radar = Radar()
        radar.add_schema(
            schema=[opts.RadarIndicatorItem(name=list(freq_dict.keys())[i], max_=list(freq_dict.values())[i]) for i in
                    range(len(list(freq_dict.keys())))])
        radar.add("", [list(freq_dict.values())])
        radar.set_global_opts(title_opts=opts.TitleOpts(title=f"{chart_type}"))
        return radar.render_embed()

    elif chart_type == '漏斗图':
        # 获取前10个高频词
        top_words = sorted(freq_dict.items(), key=lambda x: x[1], reverse=True)[:10]  # 排序并取前10
        funnel = Funnel()
        funnel.add(
            "词频漏斗",
            [opts.FunnelItem(name=word, value=freq) for word, freq in top_words]
        )
        funnel.set_global_opts(title_opts=opts.TitleOpts(title=f"{chart_type}"))
        return funnel.render_embed()

    elif chart_type == '热力图':
        heatmap = HeatMap()
        # 假设x轴是词汇，y轴是排名，value是词频
        x_axis = list(freq_dict.keys())
        y_axis = list(range(1, len(freq_dict) + 1))  # 假设y轴是排名
        value = [[x_axis.index(word), y_axis.index(rank + 1), freq] for word, freq, rank in
                 zip(list(freq_dict.keys()), list(freq_dict.values()), range(len(freq_dict)))]  # 构建热力图数据
        heatmap.add_xaxis(x_axis)
        heatmap.add_yaxis("词频", y_axis, value)  # 正确传递参数
        heatmap.set_global_opts(title_opts=opts.TitleOpts(title=f"{chart_type}"))
        return heatmap.render_embed()
    else:
        return None


# Streamlit侧边栏筛选图型
def sidebar_chart_selection():
    chart_type = st.sidebar.selectbox(
        '选择图型',
        ('条形图', '饼图', '折线图', '散点图', '雷达图', '漏斗图', '热力图')  # 更新为漏斗图
    )
    return chart_type


# 主函数
def main():
    if url:
        text_content = fetch_text_content(url)
        freq = word_frequency(text_content)

        # 展示词云
        st.subheader('词云展示')
        wordcloud_html = draw_wordcloud(freq)
        if wordcloud_html:
            html(wordcloud_html, height=600, width=1000)

        # 展示词频排名前20的词汇
        st.subheader('词频排名前20的词汇')
        top_20_words = freq.most_common(20)  # 使用Counter的most_common方法
        for word, freq in top_20_words:
            st.write(f'{word}: {freq}')

        # 侧边栏图型筛选
        chart_type = sidebar_chart_selection()
        st.sidebar.write(f'您选择的图型是：{chart_type}')

        # 绘制并展示图形
        # 将Counter对象中的top 20词频数据传递给绘图函数
        chart_html = draw_chart(chart_type, dict(top_20_words))  # 使用词频的前20个词数据
        if chart_html:
            st.subheader(f'{chart_type}展示')
            html(chart_html, height=600, width=1000)


if __name__ == '__main__':
    main()
