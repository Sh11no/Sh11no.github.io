# Chromium 内核 hook 抓包实战记录




## 前言

最近正好做到了针对安卓某 APP 内置浏览器抓包相关的东西，顺手记录一下。

目前已有的抓包解决方式可以参考 r0capture 的这个图：

https://github.com/r0ysue/r0capture/blob/main/pic/summary2.jpg

其中最为方便的是 HOOK 抓包，不需要配置或导入证书即可获得数据。网络上现有的传统的解决方案为寻找 SSL 库里的 SSL_read 和 SSL_write 函数进行 hook 抓包。这种方法确实可以实现通杀且可以抓到数据，即使是在集成了自定义 SSL 库的内置浏览器中 API 定位也相对简单，但还是存在以下缺陷：

- 数据包碎片化：由于 hook 的位置较为底层，网络通信较为紊乱，这种方式抓取的流量一般需要借助流量分析软件（如 wireshark）进行进一步分析，在 HTTP2.0 协议的加成下，多个会话的流量占用同一个 TCP 连接进行传输，这使得读写流量的拼接更为复杂繁琐，这对于需要实时批量获取数据的场景是致命的。
- 无法实现篡改：由于上面的数据包碎片化问题，在攻击者视角下，运用该方法 hook 获取发送的数据包时无法实现实时的数据包篡改和伪造。

针对上述场景，针对内置浏览器使用的 chromium 内核进行了粗略的分析，考虑在浏览器较为上层的位置截取完整的包数据。

## Chromium 网络栈

这里首先需要拿出一个经典的八股面试题：*在浏览器输入URL 地址回车后，发生了什么？*

我们并不关心无聊的八股答案，这里我们主要关注的是 Chromium 具体如何发送一个 HTTP 请求。

这里有一篇文章，懒得复读了：

https://www.cnblogs.com/bigben0123/p/12650519.html

虽然这篇文章完全忽略了对 Cache 相关的操作，但是正好我们也不关心那部分内容。

我们的目的是抓到完整的、全量的请求，所以我们需要找一个请求过程中符合以下条件的时机：

- 请求已经被构建好
- 请求还没有被交给具体的传输流

前者会导致我们无法获取完整的请求，而后者会导致请求已经根据请求协议被分流，我们只能拿到某种特定协议下的请求包而丢失其他请求。

由于确认第一点十分麻烦，所以我们期望找到的是满足第二点的最下层位置，即请求被交给传输流的前一刻。

经过几小时的坐牢我定位到了类 HttpNetworkTransaction。

https://source.chromium.org/chromium/chromium/src/+/main:net/http/http_network_transaction.cc?q=HttpNetworkTransaction&ss=chromium%2Fchromium

这里我们比较关注的是 HttpNetworkTransaction 发送请求的流程：

```cpp
int HttpNetworkTransaction::DoLoop(int result) {
  DCHECK(next_state_ != STATE_NONE);

  int rv = result;
  do {
    State state = next_state_;
    next_state_ = STATE_NONE;
    switch (state) {
      case STATE_NOTIFY_BEFORE_CREATE_STREAM:
        DCHECK_EQ(OK, rv);
        rv = DoNotifyBeforeCreateStream();
        break;
      case STATE_CREATE_STREAM:
        DCHECK_EQ(OK, rv);
        rv = DoCreateStream();
        break;
      case STATE_CREATE_STREAM_COMPLETE:
        rv = DoCreateStreamComplete(rv);
        break;
      case STATE_INIT_STREAM:
        DCHECK_EQ(OK, rv);
        rv = DoInitStream();
        break;
      case STATE_INIT_STREAM_COMPLETE:
        rv = DoInitStreamComplete(rv);
        break;
      case STATE_CONNECTED_CALLBACK:
        rv = DoConnectedCallback();
        break;
      case STATE_CONNECTED_CALLBACK_COMPLETE:
        rv = DoConnectedCallbackComplete(rv);
        break;
      case STATE_GENERATE_PROXY_AUTH_TOKEN:
        DCHECK_EQ(OK, rv);
        rv = DoGenerateProxyAuthToken();
        break;
      case STATE_GENERATE_PROXY_AUTH_TOKEN_COMPLETE:
        rv = DoGenerateProxyAuthTokenComplete(rv);
        break;
      case STATE_GENERATE_SERVER_AUTH_TOKEN:
        DCHECK_EQ(OK, rv);
        rv = DoGenerateServerAuthToken();
        break;
      case STATE_GENERATE_SERVER_AUTH_TOKEN_COMPLETE:
        rv = DoGenerateServerAuthTokenComplete(rv);
        break;
      case STATE_INIT_REQUEST_BODY:
        DCHECK_EQ(OK, rv);
        rv = DoInitRequestBody();
        break;
      case STATE_INIT_REQUEST_BODY_COMPLETE:
        rv = DoInitRequestBodyComplete(rv);
        break;
      case STATE_BUILD_REQUEST:
        DCHECK_EQ(OK, rv);
        net_log_.BeginEvent(NetLogEventType::HTTP_TRANSACTION_SEND_REQUEST);
        rv = DoBuildRequest();
        break;
      case STATE_BUILD_REQUEST_COMPLETE:
        rv = DoBuildRequestComplete(rv);
        break;
      case STATE_SEND_REQUEST:
        DCHECK_EQ(OK, rv);
        rv = DoSendRequest();
        break;
      case STATE_SEND_REQUEST_COMPLETE:
        rv = DoSendRequestComplete(rv);
        net_log_.EndEventWithNetErrorCode(
            NetLogEventType::HTTP_TRANSACTION_SEND_REQUEST, rv);
        break;
      case STATE_READ_HEADERS:
        DCHECK_EQ(OK, rv);
        net_log_.BeginEvent(NetLogEventType::HTTP_TRANSACTION_READ_HEADERS);
        rv = DoReadHeaders();
        break;
      case STATE_READ_HEADERS_COMPLETE:
        rv = DoReadHeadersComplete(rv);
        net_log_.EndEventWithNetErrorCode(
            NetLogEventType::HTTP_TRANSACTION_READ_HEADERS, rv);
        break;
      case STATE_READ_BODY:
        DCHECK_EQ(OK, rv);
        net_log_.BeginEvent(NetLogEventType::HTTP_TRANSACTION_READ_BODY);
        rv = DoReadBody();
        break;
      case STATE_READ_BODY_COMPLETE:
        rv = DoReadBodyComplete(rv);
        net_log_.EndEventWithNetErrorCode(
            NetLogEventType::HTTP_TRANSACTION_READ_BODY, rv);
        break;
      case STATE_DRAIN_BODY_FOR_AUTH_RESTART:
        DCHECK_EQ(OK, rv);
        net_log_.BeginEvent(
            NetLogEventType::HTTP_TRANSACTION_DRAIN_BODY_FOR_AUTH_RESTART);
        rv = DoDrainBodyForAuthRestart();
        break;
      case STATE_DRAIN_BODY_FOR_AUTH_RESTART_COMPLETE:
        rv = DoDrainBodyForAuthRestartComplete(rv);
        net_log_.EndEventWithNetErrorCode(
            NetLogEventType::HTTP_TRANSACTION_DRAIN_BODY_FOR_AUTH_RESTART, rv);
        break;
      default:
        NOTREACHED_IN_MIGRATION() << "bad state";
        rv = ERR_FAILED;
        break;
    }
  } while (rv != ERR_IO_PENDING && next_state_ != STATE_NONE);

  return rv;
}
```

这个流程根据状态包含了所有请求的流程，在不发生错误或重连的情况下你可以认为流程是顺序进行的（其实并不。

## RequestBody 获取

由于我们的目标是一个浏览器而不是一个网络库，在实现上 chromium 也没有必要在某个地方存储明文的整个网络请求，更多的是将 Headers、Body 等数据分散地组合在结构体里，将这些东西交给具体的传输流进行组装和传输。

在这种情况下，RequestBody 是我们最容易获取的字段。和其他我们需要的字段相比，RequestBody 直接来自前端应用。如果一个请求由 Chromium 进行创建，那么他一定是一个不含 Body 的 GET 请求，一般用于请求资源，这类资源一定不含邮 RequestBody。因此，当 RequestBody 存在的场合，该请求一定由前端主动发出，也就是说 RequestBody 的生成一定在 Chromium 之外，在进入 Chromium 时已经被**完整传入**。

在 Chromium 中，具体表现为存在一个类 UploadDataStream 在请求被创建开始时即被传入，一直层层下传到底层传输。

很遗憾，在我认为应该有 Body 信息的地方没有该信息。

```cpp
int HttpNetworkTransaction::DoInitRequestBody() {
  next_state_ = STATE_INIT_REQUEST_BODY_COMPLETE;
  int rv = OK;
  if (request_->upload_data_stream)
    rv = request_->upload_data_stream->Init(
        base::BindOnce(&HttpNetworkTransaction::OnIOComplete,
                       base::Unretained(this)),
        net_log_);
  return rv;
}
```

已知该 upload_data_stream 在传入 HttpNetworkTransaction 时就已经携带了我们想要的信息，或者我们想要的信息可以通过该结构读取。在实现具体的 hook 时，主动从一个 stream 里读数据是一个糟糕的选择：首先需要进一步分析这个数据流的工作方式，其次不能保证这个读行为是否会把数据取走导致 chromium 自己获取不到这部分数据。

因此，我们转而关注在传输流发送请求的时候如何使用这个 data_stream。

虽然前文说根据协议不同会走不同的传输流，但是他们对这个结构体的操作一定是相同的。这里选用最基础的 HTTP/1.1 协议进行分析。随机选取一个受害者类  HttpStreamParser。https://source.chromium.org/chromium/chromium/src/+/main:net/http/http_stream_parser.cc

```cpp
int HttpStreamParser::DoLoop(int result) {
  do {
    DCHECK_NE(ERR_IO_PENDING, result);
    DCHECK_NE(STATE_DONE, io_state_);
    DCHECK_NE(STATE_NONE, io_state_);
    State state = io_state_;
    io_state_ = STATE_NONE;
    switch (state) {
      case STATE_SEND_HEADERS:
        DCHECK_EQ(OK, result);
        result = DoSendHeaders();
        DCHECK_NE(STATE_NONE, io_state_);
        break;
      case STATE_SEND_HEADERS_COMPLETE:
        result = DoSendHeadersComplete(result);
        DCHECK_NE(STATE_NONE, io_state_);
        break;
      case STATE_SEND_BODY:
        DCHECK_EQ(OK, result);
        result = DoSendBody();
        DCHECK_NE(STATE_NONE, io_state_);
        break;
      case STATE_SEND_BODY_COMPLETE:
        result = DoSendBodyComplete(result);
        DCHECK_NE(STATE_NONE, io_state_);
        break;
      case STATE_SEND_REQUEST_READ_BODY_COMPLETE:
        result = DoSendRequestReadBodyComplete(result);
        DCHECK_NE(STATE_NONE, io_state_);
        break;
      case STATE_SEND_REQUEST_COMPLETE:
        result = DoSendRequestComplete(result);
        break;
      case STATE_READ_HEADERS:
        net_log_.BeginEvent(NetLogEventType::HTTP_STREAM_PARSER_READ_HEADERS);
        DCHECK_GE(result, 0);
        result = DoReadHeaders();
        break;
      case STATE_READ_HEADERS_COMPLETE:
        result = DoReadHeadersComplete(result);
        net_log_.EndEventWithNetErrorCode(
            NetLogEventType::HTTP_STREAM_PARSER_READ_HEADERS, result);
        break;
      case STATE_READ_BODY:
        DCHECK_GE(result, 0);
        result = DoReadBody();
        break;
      case STATE_READ_BODY_COMPLETE:
        result = DoReadBodyComplete(result);
        break;
      default:
        NOTREACHED_IN_MIGRATION();
        break;
    }
  } while (result != ERR_IO_PENDING &&
           (io_state_ != STATE_DONE && io_state_ != STATE_NONE));

  return result;
}
```

关心的 SendBody

```cpp
int HttpStreamParser::DoSendBody() {
  if (request_body_send_buf_->BytesRemaining() > 0) {
    io_state_ = STATE_SEND_BODY_COMPLETE;
    return stream_socket_->Write(
        request_body_send_buf_.get(), request_body_send_buf_->BytesRemaining(),
        io_callback_, NetworkTrafficAnnotationTag(traffic_annotation_));
  }

  if (upload_data_stream_->is_chunked() && sent_last_chunk_) {
    // Finished sending the request.
    io_state_ = STATE_SEND_REQUEST_COMPLETE;
    return OK;
  }

  request_body_read_buf_->Clear();
  io_state_ = STATE_SEND_REQUEST_READ_BODY_COMPLETE;
  return upload_data_stream_->Read(
      request_body_read_buf_.get(), request_body_read_buf_->capacity(),
      base::BindOnce(&HttpStreamParser::OnIOComplete,
                     weak_ptr_factory_.GetWeakPtr()));
}
```

可以发现当一个传输流准备发送 RequestBody 时，会先调用 UploadDataStream::Read 读取 RequestBody 再进行上传。这里产生了我们的第一个受害者函数：

```cpp
int UploadDataStream::Read(IOBuffer* buf,
                           int buf_len,
                           CompletionOnceCallback callback) {
  DCHECK(!callback.is_null() || IsInMemory());
  DCHECK(initialized_successfully_);
  DCHECK_GT(buf_len, 0);

  net_log_.BeginEvent(NetLogEventType::UPLOAD_DATA_STREAM_READ,
                      [&] { return CreateReadInfoParams(current_position_); });

  int result = 0;
  if (!is_eof_)
    result = ReadInternal(buf, buf_len);

  if (result == ERR_IO_PENDING) {
    DCHECK(!IsInMemory());
    callback_ = std::move(callback);
  } else {
    OnReadCompleted(result);
  }

  return result;
}
```

hook 该函数，当该函数被调用时读取 IOBuffer 即可拿到 RequestBody。

## RequestHeader 获取

还是从 DoLoop 开始分析：

```cpp
int HttpNetworkTransaction::DoBuildRequest() {
  next_state_ = STATE_BUILD_REQUEST_COMPLETE;
  headers_valid_ = false;

  // This is constructed lazily (instead of within our Start method), so that
  // we have proxy info available.
  if (request_headers_.IsEmpty()) {
    bool using_http_proxy_without_tunnel = UsingHttpProxyWithoutTunnel();
    return BuildRequestHeaders(using_http_proxy_without_tunnel);
  }

  return OK;
}
int HttpNetworkTransaction::BuildRequestHeaders(
    bool using_http_proxy_without_tunnel) {
  request_headers_.SetHeader(HttpRequestHeaders::kHost,
                             GetHostAndOptionalPort(request_->url));

  // For compat with HTTP/1.0 servers and proxies:
  if (using_http_proxy_without_tunnel) {
    request_headers_.SetHeader(HttpRequestHeaders::kProxyConnection,
                               "keep-alive");
  } else {
    request_headers_.SetHeader(HttpRequestHeaders::kConnection, "keep-alive");
  }

  // Add a content length header?
  if (request_->upload_data_stream) {
    if (request_->upload_data_stream->is_chunked()) {
      request_headers_.SetHeader(
          HttpRequestHeaders::kTransferEncoding, "chunked");
    } else {
      request_headers_.SetHeader(
          HttpRequestHeaders::kContentLength,
          base::NumberToString(request_->upload_data_stream->size()));
    }
  } else if (request_->method == "POST" || request_->method == "PUT") {
    // An empty POST/PUT request still needs a content length.  As for HEAD,
    // IE and Safari also add a content length header.  Presumably it is to
    // support sending a HEAD request to an URL that only expects to be sent a
    // POST or some other method that normally would have a message body.
    // Firefox (40.0) does not send the header, and RFC 7230 & 7231
    // specify that it should not be sent due to undefined behavior.
    request_headers_.SetHeader(HttpRequestHeaders::kContentLength, "0");
  }

  // Honor load flags that impact proxy caches.
  if (request_->load_flags & LOAD_BYPASS_CACHE) {
    request_headers_.SetHeader(HttpRequestHeaders::kPragma, "no-cache");
    request_headers_.SetHeader(HttpRequestHeaders::kCacheControl, "no-cache");
  } else if (request_->load_flags & LOAD_VALIDATE_CACHE) {
    request_headers_.SetHeader(HttpRequestHeaders::kCacheControl, "max-age=0");
  }

  if (ShouldApplyProxyAuth() && HaveAuth(HttpAuth::AUTH_PROXY))
    auth_controllers_[HttpAuth::AUTH_PROXY]->AddAuthorizationHeader(
        &request_headers_);
  if (ShouldApplyServerAuth() && HaveAuth(HttpAuth::AUTH_SERVER))
    auth_controllers_[HttpAuth::AUTH_SERVER]->AddAuthorizationHeader(
        &request_headers_);

  if (net::features::kIpPrivacyAddHeaderToProxiedRequests.Get() &&
      proxy_info_.is_for_ip_protection()) {
    CHECK(!proxy_info_.is_direct() ||
          net::features::kIpPrivacyDirectOnly.Get());
    if (!proxy_info_.is_direct()) {
      request_headers_.SetHeader("IP-Protection", "1");
    }
  }

  request_headers_.MergeFrom(request_->extra_headers);

  if (modify_headers_callbacks_) {
    modify_headers_callbacks_.Run(&request_headers_);
  }

  response_.did_use_http_auth =
      request_headers_.HasHeader(HttpRequestHeaders::kAuthorization) ||
      request_headers_.HasHeader(HttpRequestHeaders::kProxyAuthorization);
  return OK;
}
```

其实这里很明显了，我们的下一个受害者函数是 HttpRequestHeaders::SetHeader。

```cpp
void HttpRequestHeaders::SetHeader(std::string_view key,
                                   std::string_view value) {
  SetHeader(key, std::string(value));
}
```

## Request 组装

在前文我们获取了所有的 Request 信息，但是这两个信息获取的位置可以说是毫不相关，甚至所有的 RequestHeaders 都是碎片。我们需要一个方法把这些信息组装起来。

这里有一个好东西：

```cpp
int HttpNetworkTransaction::Start(const HttpRequestInfo* request_info,
                                  CompletionOnceCallback callback,
                                  const NetLogWithSource& net_log) {
  if (request_info->load_flags & LOAD_ONLY_FROM_CACHE)
    return ERR_CACHE_MISS;

  DCHECK(request_info->traffic_annotation.is_valid());
  DCHECK(request_info->IsConsistent());
  net_log_ = net_log;
  request_ = request_info;
  url_ = request_->url;
  network_anonymization_key_ = request_->network_anonymization_key;
#if BUILDFLAG(ENABLE_REPORTING)
  // Store values for later use in NEL report generation.
  request_method_ = request_->method;
  request_->extra_headers.GetHeader(HttpRequestHeaders::kReferer,
                                    &request_referrer_);
  request_->extra_headers.GetHeader(HttpRequestHeaders::kUserAgent,
                                    &request_user_agent_);
  request_reporting_upload_depth_ = request_->reporting_upload_depth;
  start_timeticks_ = base::TimeTicks::Now();
#endif  // BUILDFLAG(ENABLE_REPORTING)

  if (request_->idempotency == IDEMPOTENT ||
      (request_->idempotency == DEFAULT_IDEMPOTENCY &&
       HttpUtil::IsMethodSafe(request_info->method))) {
    can_send_early_data_ = true;
  }

  if (request_->load_flags & LOAD_PREFETCH) {
    response_.unused_since_prefetch = true;
  }

  if (request_->load_flags & LOAD_RESTRICTED_PREFETCH) {
    DCHECK(response_.unused_since_prefetch);
    response_.restricted_prefetch = true;
  }

  next_state_ = STATE_NOTIFY_BEFORE_CREATE_STREAM;
  int rv = DoLoop(OK);
  if (rv == ERR_IO_PENDING)
    callback_ = std::move(callback);

  // This always returns ERR_IO_PENDING because DoCreateStream() does, but
  // GenerateNetworkErrorLoggingReportIfError() should be called here if any
  // other net::Error can be returned.
  DCHECK_EQ(rv, ERR_IO_PENDING);
  return rv;
}
```

众所周知，在实际的类方法调用时，会隐藏地传入第一个参数 this，表示当前的类对象地址。而 HttpNetworkTransaction 类中将上述两个类实例当作了成员变量，我们只需要在该类被创建时建立上述两个类实例到 HttpNetworkTransaction 的连接映射，即可将他们组合到一起。这个类也可以帮助我们组合后续的 Response。

请求的 url 和请求的 method 也在此处入参获取。

## ResponseHeaders 获取

Request 是散装的，Response 总应该是完整读取的吧？

其实不然，Chromium 在读取完 ResponseHeaders 之后，才会通知上层，由上层再主动下来读取 ResponseBody。

但是确实，我们可以一次性获得完整的 ResponseHeader。

```cpp
int HttpNetworkTransaction::DoReadHeaders() {
  next_state_ = STATE_READ_HEADERS_COMPLETE;
  return stream_->ReadResponseHeaders(io_callback_);
}
```

stream 随使用的请求协议而变化，这不是很好，我们不如关心 ResponseHeader 的解析逻辑。

在 HttpNetworkTransaction 类成员里，我们看到了类成员 HttpResponseInfo 的成员 HttpResponseHeaders 的构造函数。

```cpp
HttpResponseHeaders::HttpResponseHeaders(
    BuilderPassKey,
    HttpVersion version,
    std::string_view status,
    base::span<const std::pair<std::string_view, std::string_view>> headers)
    : http_version_(version) {
  // This must match the behaviour of Parse(). We don't use Parse() because
  // avoiding the overhead of parsing is the point of this constructor.

  std::string formatted_status;
  formatted_status.reserve(status.size() + 1);  // ParseStatus() may add a space
  response_code_ = ParseStatus(status, formatted_status);

  // First calculate how big the output will be so that we can allocate the
  // right amount of memory.
  size_t expected_size = 8;  // "HTTP/x.x"
  expected_size += formatted_status.size();
  expected_size += 1;  // "\\0"
  size_t expected_parsed_size = 0;

  // Track which headers (by index) have a comma in the value. Since bools are
  // only 1 byte, we can afford to put 100 of them on the stack and avoid
  // allocating more memory 99.9% of the time.
  absl::InlinedVector<bool, 100> header_contains_comma;
  for (const auto& [key, value] : headers) {
    expected_size += key.size();
    expected_size += 1;  // ":"
    expected_size += value.size();
    expected_size += 1;  // "\\0"
    // It's okay if we over-estimate the size of `parsed_`, so treat all ','
    // characters as if they might split the value to avoid parsing the value
    // carefully here.
    const size_t comma_count = base::ranges::count(value, ',') + 1;
    expected_parsed_size += comma_count;
    header_contains_comma.push_back(comma_count);
  }
  expected_size += 1;  // "\\0"
  raw_headers_.reserve(expected_size);
  parsed_.reserve(expected_parsed_size);

  // Now fill in the output.
  const uint16_t major = version.major_value();
  const uint16_t minor = version.minor_value();
  CHECK_LE(major, 9);
  CHECK_LE(minor, 9);
  raw_headers_.append("HTTP/");
  raw_headers_.push_back('0' + major);
  raw_headers_.push_back('.');
  raw_headers_.push_back('0' + minor);
  raw_headers_.append(formatted_status);
  raw_headers_.push_back('\\0');
  // It is vital that `raw_headers_` iterators are not invalidated after this
  // point.
  const char* const data_at_start = raw_headers_.data();
  size_t index = 0;
  for (const auto& [key, value] : headers) {
    CheckDoesNotHaveEmbeddedNulls(key);
    CheckDoesNotHaveEmbeddedNulls(value);
    // Because std::string iterators are random-access, end() has to point to
    // the position where the next character will be appended.
    const auto name_begin = raw_headers_.cend();
    raw_headers_.append(key);
    const auto name_end = raw_headers_.cend();
    raw_headers_.push_back(':');
    auto values_begin = raw_headers_.cend();
    raw_headers_.append(value);
    auto values_end = raw_headers_.cend();
    raw_headers_.push_back('\\0');
    // The HTTP/2 standard disallows header values starting or ending with
    // whitespace (RFC 9113 8.2.1). Hopefully the same is also true of HTTP/3.
    // TODO(crbug.com/40282642): Validate that our implementations
    // actually enforce this constraint and change this TrimLWS() to a DCHECK.
    HttpUtil::TrimLWS(&values_begin, &values_end);
    AddHeader(name_begin, name_end, values_begin, values_end,
              header_contains_comma[index] ? ContainsCommas::kYes
                                           : ContainsCommas::kNo);
    ++index;
  }
  raw_headers_.push_back('\\0');
  CHECK_EQ(expected_size, raw_headers_.size());
  CHECK_EQ(data_at_start, raw_headers_.data());
  DCHECK_LE(parsed_.size(), expected_parsed_size);

  DCHECK_EQ('\\0', raw_headers_[raw_headers_.size() - 2]);
  DCHECK_EQ('\\0', raw_headers_[raw_headers_.size() - 1]);
}
```

可以发现该类在构造时把整个 header 传入了 raw_headers_，这是一个 string 变量，也就是说我们可以在 Headers 被读取完之后的任意时机直接从 HttpNetworkTransaction 的 this 地址找到这些信息。

## ResponseBody 获取

这里的难点本来在于如何确定 ResponseBody 已经被全部读取完成，但是 chromium 的垃圾回收帮我们解决了这一难题：

```cpp
int HttpNetworkTransaction::DoReadBody() {
  DCHECK(read_buf_.get());
  DCHECK_GT(read_buf_len_, 0);
  DCHECK(stream_ != nullptr);

  next_state_ = STATE_READ_BODY_COMPLETE;
  return stream_->ReadResponseBody(
      read_buf_.get(), read_buf_len_, io_callback_);
}

int HttpNetworkTransaction::DoReadBodyComplete(int result) {
  // We are done with the Read call.
  bool done = false;
  if (result <= 0) {
    DCHECK_NE(ERR_IO_PENDING, result);
    done = true;
  }

  // Clean up connection if we are done.
  if (done) {
    // Note: Just because IsResponseBodyComplete is true, we're not
    // necessarily "done".  We're only "done" when it is the last
    // read on this HttpNetworkTransaction, which will be signified
    // by a zero-length read.
    // TODO(mbelshe): The keep-alive property is really a property of
    //    the stream.  No need to compute it here just to pass back
    //    to the stream's Close function.
    bool keep_alive =
        stream_->IsResponseBodyComplete() && stream_->CanReuseConnection();

    stream_->Close(!keep_alive);
    // Note: we don't reset the stream here.  We've closed it, but we still
    // need it around so that callers can call methods such as
    // GetUploadProgress() and have them be meaningful.
    // TODO(mbelshe): This means we closed the stream here, and we close it
    // again in ~HttpNetworkTransaction.  Clean that up.

    // The next Read call will return 0 (EOF).

    // This transaction was successful. If it had been retried because of an
    // error with an alternative service, mark that alternative service broken.
    if (!enable_alternative_services_ &&
        retried_alternative_service_.protocol != kProtoUnknown) {
      HistogramBrokenAlternateProtocolLocation(
          BROKEN_ALTERNATE_PROTOCOL_LOCATION_HTTP_NETWORK_TRANSACTION);
      session_->http_server_properties()->MarkAlternativeServiceBroken(
          retried_alternative_service_, network_anonymization_key_);
    }

#if BUILDFLAG(ENABLE_REPORTING)
    GenerateNetworkErrorLoggingReport(result);
#endif  // BUILDFLAG(ENABLE_REPORTING)
  }

  // Clear these to avoid leaving around old state.
  read_buf_ = nullptr;
  read_buf_len_ = 0;

  return result;
}
```

body 被读入 read_buf ，在读入结束后该指针会被清空。

也就是说，我们 hook HttpNetworkTransaction::DoReadBodyComplete，在该函数进入之前存下 read_buf 指针，在该函数退出之后若该指针被清空，则说明读取已完成，这时候我们可以从先前存下的指针位置读取完整的 Body。

为了减少工作量，在这个阶段所有的 ResponseHeader 一定已经被全部读取完成，我们可以在该函数的 hook 逻辑中顺手打印。

## 定位和实现

到这里我们的实现思路已经很明显了：

- Hook 函数 HttpNetworkTransaction::Start
  - 从入参获取 url 和 method。
  - 建立 HttpRequestHeaders -> HttpNetworkTransaction 映射。
  - 建立 UploadDataStream -> HttpNetworkTransaction 映射。
- Hook 函数 UploadDataStream::Read
  - 读取入参 IOBuffer，获取 RequestBody。
  - 根据前面建立的映射，将 RequestBody 关联到 HttpNetworkTransaction 。
- Hook 函数 HttpRequestHeaders::SetHeader
  - 读取入参 key 和 value。
  - 将本次添加的 Header 关联到 HttpNetworkTransaction。
- Hook 函数 HttpNetworkTransaction::DoReadBodyComplete
  - 判断请求是否完成，若未完成则继续接收。
  - 根据调用前缓存的 read_buf_ 获取 ResponseBody
    - 根据 content encoding 进行解压（如 gzip）
  - 寻找 HttpNetworkTransaction->responseinfo->responseheaders->raw_headers_ 获取完整的 RequestHeaders

具体上述类成员偏移和函数偏移确定方式不公开，相信各位读者都有自己的理解。

项目代码：如果你想要，那你就得自己来写。

