# -*- coding: utf-8 -*-

import logging

import nagiosplugin as np

from check_pa.xml_reader import XMLReader, Finder

_log = logging.getLogger('nagiosplugin')


def create_check(args):
    """
    Creates and configures a check for the reports command.

    :return: the bgp check.
    """
    return np.Check(
        Reports(args.host, args.token, args.report, args.name, args.type),
        np.ScalarContext('reports'),
        ReportsSummary())


class Reports(np.Resource):
    """
    Will fetch the reports informations  from the REST API and returns
    """

    def __init__(self, host, token, reports, rname, rtype):
        self.host = host
        self.token = token
        self.cmd = reports
        self.rname = rname
        self.rtype = rtype
        self.xml_obj = XMLReader(self.host, self.token, self.cmd)

    def probe(self):
        """
        Query the REST-API and create reports metrics.

        :return: reports metric.
        """
        _log.info('Reading XML from: %s', self.xml_obj.build_request_url(True))
        soup = self.xml_obj.report()
        result = soup.result
        #_log.debug('XML Result: \n%s', str(result))
        attrs = []
        for item in result.find_all('entry'):
            rname = str(Finder.find_item(item, self.rname))
            rvalue = int(Finder.find_item(item, self.rtype))
            yield np.Metric('%s' % rname, rvalue, context='reports')

class ReportsSummary(np.Summary):
    def ok(self, results):
        l = []
        for result in results.results:
            s = '%s: %s' % (result.metric.name, result.metric.value)
            _log.debug('Add result %r', s)
            l.append(s)
        _log.debug('Result count: %d' % len(l))
        output = "\n".join(l)
        return str(output)
