# 共享模型

## 基础版

在38G中英混合语料（中英比为3:5）上训练的两个模型：

|  | vocab size | 压缩率 (bytes/token) |
| :----: | :----: | :----: |
| [bytepiece_80k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece_80k.zip) | 79,896 | 5.09 |
| [bytepiece_160k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece_160k.zip) | 159,896 | 5.34 |

## 增强版

在185G混合语料（中、英、代码语料比为3:5:0.5）上训练的模型：

|  | vocab size | 压缩率 (bytes/token) |
| :----: | :----: | :----: |
| [bytepiece.plus.40k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.plus.40k.zip) | 39,843 | 4.63 |
| [bytepiece.plus.80k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.plus.80k.zip) | 79,812 | 5.13 |
| [bytepiece.plus.160k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.plus.160k.zip) | 159,846 | 5.56 |
| [bytepiece.plus.240k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.plus.240k.zip) | 239,858 | 5.74 |
| [bytepiece.plus.320k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.plus.320k.zip) | 319,768 | 5.83 |
| [bytepiece.id.plus.40k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.id.plus.40k.zip) | 39,857 | 4.51 |
| [bytepiece.id.plus.80k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.id.plus.80k.zip) | 79,827 | 4.96 |
| [bytepiece.id.plus.160k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.id.plus.160k.zip) | 159,868 | 5.34 |
| [bytepiece.id.plus.240k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.id.plus.240k.zip) | 239,888 | 5.50 |
| [bytepiece.id.plus.320k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.id.plus.320k.zip) | 319,808 | 5.58 |
| [bytepiece.eu.plus.40k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.eu.plus.40k.zip) | 39,842 | 4.59 |
| [bytepiece.eu.plus.80k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.eu.plus.80k.zip) | 79,816 | 5.11 |
| [bytepiece.eu.plus.160k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.eu.plus.160k.zip) | 159,831 | 5.57 |
| [bytepiece.eu.plus.240k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.eu.plus.240k.zip) | 239,862 | 5.76 |
| [bytepiece.eu.plus.320k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.eu.plus.320k.zip) | 319,767 | 5.86 |
| [bytepiece.id.eu.plus.40k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.id.eu.plus.40k.zip) | 39,857 | 4.65 |
| [bytepiece.id.eu.plus.80k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.id.eu.plus.80k.zip) | 79,829 | 5.08 |
| [bytepiece.id.eu.plus.160k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.id.eu.plus.160k.zip) | 159,869 | 5.41 |
| [bytepiece.id.eu.plus.240k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.id.eu.plus.240k.zip) | 239,884 | 5.55 |
| [bytepiece.id.eu.plus.320k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.id.eu.plus.320k.zip) | 319,811 | 5.61 |

其中id指的是isolate digits，即将阿拉伯数字单独分开；eu指的是eusure unicode，保证每一个多字节token都可以decode为unicode。可以看到，在固定的语料配比上，当vocab_size到大一定程度后，增大vocab_size也无法带来明显的压缩率提高。

## 结巴版

|  | vocab size |
| :----: | :----: |
| [bytepiece.jieba.410k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.jieba.410k.zip) | 409,629 |

从[jieba](https://github.com/fxsjy/jieba)的词表转换而来，主要保留了jieba的原词表和词频，并融合了[bytepiece.eu.plus.320k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.eu.plus.320k.zip)的标点、单字和英文，文本分词效果基本上会跟jieba一致，但英文和数字可能会略有不同（毕竟jieba本身不是面向tokenizer设计）。

转换该模型的目的，是得到一个中文分词结果跟我们常规认知的中文分词一致的tokenizer，而不是追求压缩率，可以理解为这是一个简单的有监督bytepiece模型，也可以理解为一个带有id转换功能的jieba分词。bytepiece版本分词速度大概是原始jieba的两倍，跟[jieba_fast](https://github.com/deepcs233/jieba_fast)持平。
