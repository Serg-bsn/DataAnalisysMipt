# Обнаружение статистически значимых отличий в уровнях экспрессии генов больных раком

# Это задание поможет вам лучше разобраться в методах множественной проверки гипотез и позволит применить
# ваши знания на данных из реального биологического исследования.

# В этом задании вы:
#    вспомните, что такое t-критерий Стьюдента и для чего он применяется
#    сможете применить технику множественной проверки гипотез и увидеть собственными глазами, как она работает
#       на реальных данных
#    почувствуете разницу в результатах применения различных методов поправки на множественную проверку

# Основные библиотеки и используемые методы:
#   Библиотека scipy и основные статистические функции:
#       http://docs.scipy.org/doc/scipy/reference/stats.html#statistical-functions
#   Библиотека statmodels для методов коррекции при множественном сравнении:
#       http://statsmodels.sourceforge.net/devel/stats.html
# Статья, в которой рассматриваются примеры использования statsmodels для множественной проверки гипотез:
#       http://jpktd.blogspot.ru/2013/04/multiple-testing-p-value-corrections-in.html

# Описание используемых данных
# Данные для этой задачи взяты из исследования, проведенного в Stanford School of Medicine.
# В исследовании была предпринята попытка выявить набор генов, которые позволили бы более точно
# диагностировать возникновение рака груди на самых ранних стадиях.
# В эксперименте принимали участие 24 человек, у которых не было рака груди (normal), 25 человек, у которых это
# заболевание было диагностировано на ранней стадии (early neoplasia), и 23 человека с сильно выраженными
# симптомами (cancer).
# Ученые провели секвенирование биологического материала испытуемых, чтобы понять, какие из этих генов наиболее
# активны в клетках больных людей.
# Секвенирование — это определение степени активности генов в анализируемом образце с помощью подсчёта
# количества соответствующей каждому гену РНК.
# В данных для этого задания вы найдете именно эту количественную меру активности каждого из 15748 генов у
# каждого из 72 человек, принимавших участие в эксперименте.
# Вам нужно будет определить те гены, активность которых у людей в разных стадиях заболевания отличается
# статистически значимо.
# Кроме того, вам нужно будет оценить не только статистическую, но и практическую значимость этих результатов,
# которая часто используется в подобных исследованиях.
# Диагноз человека содержится в столбце под названием "Diagnosis".

# Практическая значимость изменения
# Цель исследований — найти гены, средняя экспрессия которых отличается не только статистически значимо,
# но и достаточно сильно. В экспрессионных исследованиях для этого часто используется метрика, которая
# называется fold change (кратность изменения). Определяется она следующим образом:
#    Fc(C,T)=T/C,T>C; −C/T,T<C
#    где C,T — средние значения экспрессии гена в control и treatment группах соответственно.
# По сути, fold change показывает, во сколько раз отличаются средние двух выборок.

#%%
def write_answer(file_name, answer):
    with open(file_name, "w") as fout: #..\..\Results\
        fout.write(str(answer))
#%%
import pandas as pd
import numpy as np
import scipy
from statsmodels.stats.weightstats import *
%pylab inline
frame = pd.read_csv("gene_high_throughput_sequencing.csv", sep=",", header=0)
frame.head()


# Инструкции к решению задачи
# Задание состоит из трёх частей. Если не сказано обратное, то уровень значимости нужно принять равным 0.05.


# Часть 1: применение t-критерия Стьюдента
# В первой части вам нужно будет применить критерий Стьюдента для проверки гипотезы о равенстве средних в двух
# независимых выборках. Применить критерий для каждого гена нужно будет дважды:
#   для групп normal (control) и early neoplasia (treatment)
#   для групп early neoplasia (control) и cancer (treatment)
# В качестве ответа в этой части задания необходимо указать количество статистически значимых отличий, которые
# вы нашли с помощью t-критерия Стьюдента, то есть число генов, у которых p-value этого теста оказался меньше,
# чем уровень значимости.
#%%
print "Diagnosis values: "
print set(frame["Diagnosis"])
#%%
normal_neoplasia = frame[frame["Diagnosis"] == "normal"].drop(["Patient_id", "Diagnosis"], axis=1)
early_neoplasia = frame[frame["Diagnosis"] == "early neoplasia"].drop(["Patient_id", "Diagnosis"], axis=1)
cancer = frame[frame["Diagnosis"] == "cancer"].drop(["Patient_id", "Diagnosis"], axis=1)
data_columns = frame.columns.drop(["Patient_id", "Diagnosis"])
print "Normal neoplasia count: %i\tRow size: %i" % normal_neoplasia.shape
print "Early neoplasia count: %i\tRow size: %i" % early_neoplasia.shape
print "Cancer count: %i\tRow size: %i" % cancer.shape
# Для того, чтобы использовать двухвыборочный критерий Стьюдента, убедимся, что распределения в выборках
# существенно не отличаются от нормальных.
# Критерий Шапиро-Уилка:
# H0: среднее значение РНК в генах распределено нормально
# H1: не нормально.
#%%
print "Shapiro-Wilk normality test, W-statistic:"
for col_name in data_columns:
    print "\tNormal neoplasia \"" + col_name + "\": %f, p-value: %f" % stats.shapiro(normal_neoplasia[col_name])
    print "\tEarly neoplasia \"" + col_name + "\": %f, p-value: %f" % stats.shapiro(early_neoplasia[col_name])
    print "\tCancer  \"" + col_name + "\": %f, p-value: %f" % stats.shapiro(cancer[col_name])
# Не все значения распределены нормально

# Критерий Стьюдента:
# H0: средние значения РНК в генах распределено одинаково.
# H1: не одинаково.
#%%
def compare_genes_diffs(right, left, columns):
    return [scipy.stats.ttest_ind(right[col_name], left[col_name], equal_var = False).pvalue for col_name in columns]
#%%
normal_early_diff_genes = compare_genes_diffs(normal_neoplasia, early_neoplasia, data_columns)
normal_early_diff_genes_count = len(filter(lambda pvalue: pvalue < 0.05, normal_early_diff_genes))
print "T-Student test normal vs early neoplasia different distributed genes: %i" % normal_early_diff_genes_count
write_answer("normal_early.txt", normal_early_diff_genes_count)
#%%
early_cancer_diff_genes = compare_genes_diffs(early_neoplasia, cancer, data_columns)
early_cancer_diff_genes_count = len(filter(lambda pvalue: pvalue < 0.05, early_cancer_diff_genes))
print "T-Student test early neoplasia vs cancer different distributed genes: %i" % early_cancer_diff_genes_count
write_answer("early_cancer.txt", early_cancer_diff_genes_count)

# Часть 2: поправка методом Холма
# Для этой части задания вам понадобится модуль multitest из statsmodels.
#%%
import statsmodels.stats.multitest as smm
# В этой части задания нужно будет применить поправку Холма для получившихся двух наборов достигаемых уровней
# значимости из предыдущей части. Обратите внимание, что поскольку вы будете делать поправку для каждого из
# двух наборов p-value отдельно, то проблема, связанная с множественной проверкой останется.
# Для того, чтобы ее устранить, достаточно воспользоваться поправкой Бонферрони, то есть использовать уровень
# значимости 0.05 / 2 вместо 0.05 для дальнейшего уточнения значений p-value c помощью метода Холма.
# В качестве ответа к этому заданию требуется ввести количество значимых отличий в каждой группе после того,
# как произведена коррекция Холма-Бонферрони. Причем это число нужно ввести с учетом практической значимости:
# посчитайте для каждого значимого изменения fold change и выпишите в ответ число таких значимых изменений,
# абсолютное значение fold change которых больше, чем 1.5.

# Обратите внимание, что
#    применять поправку на множественную проверку нужно ко всем значениям достигаемых уровней значимости,
#       а не только для тех, которые меньше значения уровня доверия.
#    при использовании поправки на уровне значимости 0.025 меняются значения достигаемого уровня значимости,
#       но не меняется значение уровня доверия (то есть для отбора значимых изменений скорректированные значения
#       уровня значимости нужно сравнивать с порогом 0.025, а не 0.05)!

#%%
(reject_n_e,pvalues_normal_early_holm,alphac_n_e_sidak,alphac_n_e_bonf) = smm.multipletests(
    normal_early_diff_genes,
    alpha=0.025,
    method="holm"
)
print len(filter(lambda pvalue: pvalue < 0.05, pvalues_normal_early_holm))
#%%
(reject_e_c,pvalues_early_cancer_holm,alphac_e_c_sidak,alphac_e_c_bonf) = smm.multipletests(
    early_cancer_diff_genes,
    alpha=0.025,
    method="holm")
print len(filter(lambda pvalue: pvalue < 0.05, pvalues))
#%%
def calc_fold_change(control, treatment, column):
    ctrl_mean = control[column].mean()
    trtmnt_mean = treatment[column].mean()
    return abs(trtmnt_mean/ctrl_mean if trtmnt_mean > ctrl_mean else -ctrl_mean/trtmnt_mean)
def calculate_fold_changes(control_data, treatment_data, pvalues, columns, alpha):
    return map(
        lambda (column, pvalue): calc_fold_change(control_data, treatment_data, column),
        filter(
            lambda (column, pvalue): pvalue < alpha,
            zip(columns, pvalues)
        )
    )
#%%
folds_normal_early = calculate_fold_changes(
    normal_neoplasia,
    early_neoplasia,
    pvalues_normal_early_holm,
    data_columns,
    0.025
)
folds_normal_early_meaningful_count = len(filter(lambda fld: fld > 1.5, folds_normal_early))
print "Normal-early after holm fix: %i" % folds_normal_early_meaningful_count
write_answer("normal_early_holm.txt", folds_normal_early_meaningful_count)
#%%
folds_early_cancer = calculate_fold_changes(
    early_neoplasia,
    cancer,
    pvalues_early_cancer_holm,
    data_columns,
    0.025
)
folds_early_cancer_meaningful_count = len(filter(lambda fld: fld > 1.5, folds_early_cancer))
print "Early-cancer after holm fix: %i" % folds_normal_early_meaningful_count
write_answer("early_cancer_holm.txt", folds_early_cancer_meaningful_count)


# Часть 3: поправка методом Бенджамини-Хохберга
# Данная часть задания аналогична второй части за исключением того, что нужно будет использовать метод
# Бенджамини-Хохберга.
# Обратите внимание, что методы коррекции, которые контролируют FDR, допускает больше ошибок первого рода и
# имеют большую мощность, чем методы, контролирующие FWER. Большая мощность означает, что эти методы будут
# совершать меньше ошибок второго рода (то есть будут лучше улавливать отклонения от H0, когда они есть, и
# будут чаще отклонять H0, когда отличий нет).
# В качестве ответа к этому заданию требуется ввести количество значимых отличий в каждой группе после того,
# как произведена коррекция Бенджамини-Хохберга, причем так же, как и во второй части, считать только такие
# отличия, у которых abs(fold change) > 1.5.
#%%
(reject_n_e,pvalues_normal_early_hohberg,alphac_n_e_sidak,alphac_n_e_bonf) = smm.multipletests(
    normal_early_diff_genes,
    alpha=0.05,
    method="fdr_bh"
)
print len(filter(lambda pvalue: pvalue < 0.05, pvalues_normal_early_hohberg))
#%%
(reject_e_c,pvalues_early_cancer_hohberg,alphac_e_c_sidak,alphac_e_c_bonf) = smm.multipletests(
    early_cancer_diff_genes,
    alpha=0.05,
    method="fdr_bh")
print len(filter(lambda pvalue: pvalue < 0.05, pvalues_early_cancer_hohberg))
#%%
folds_normal_early_hohberg = calculate_fold_changes(
    normal_neoplasia,
    early_neoplasia,
    pvalues_normal_early_hohberg,
    data_columns,
    0.05
)
folds_normal_early_meaningful_count_hohberg = len(filter(lambda fld: fld > 1.5, folds_normal_early_hohberg))
print "Normal-early after benjamini-hohberg fix: %i" % folds_normal_early_meaningful_count_hohberg
write_answer("normal_early_hohberg.txt", folds_normal_early_meaningful_count_hohberg)
#%%
folds_early_cancer_hohberg = calculate_fold_changes(
    early_neoplasia,
    cancer,
    pvalues_early_cancer_hohberg,
    data_columns,
    0.05
)
folds_early_cancer_meaningful_count_hohberg = len(filter(lambda fld: fld > 1.5, folds_early_cancer_hohberg))
print "Early-cancer after benjamini-hohberg fix: %i" % folds_early_cancer_meaningful_count_hohberg
write_answer("early_cancer_hohberg.txt", folds_early_cancer_meaningful_count_hohberg)


# P.S. Вспомните, какое значение имеет уровень значимости α в каждой из поправок: Холма и Бенджамини-Хохберга.
# Одинаковый ли смысл имеет уровень значимости в каждой из поправок?
