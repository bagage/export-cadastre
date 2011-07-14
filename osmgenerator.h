/* This file is part of Qadastre
 * Copyright (C) 2010 Pierre Ducroquet <pinaraf@pinaraf.info>
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Library General Public
 * License as published by the Free Software Foundation; either
 * version 2 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Library General Public License for more details.
 *
 * You should have received a copy of the GNU Library General Public License
 * along with this library; see the file COPYING.LIB.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
 * Boston, MA 02110-1301, USA.
 */

#ifndef OSMGENERATOR_H
#define OSMGENERATOR_H

#include <QObject>
#include <QList>
#include <QPainterPath>
#include <QMap>
#include <QPointF>
#include <proj_api.h>
#include "vectorpath.h"
#include "graphicproducer.h"

struct OSMPath {
    VectorPath path;
    QMap<QString, QString> tags;
    QList<QList<int> > points_position; // One list per polygon in the path

    bool operator==(const OSMPath &other) const;
};

class OSMGenerator : public QObject
{
    Q_OBJECT
public:
    explicit OSMGenerator(const QString &bbox, const bool lands, QObject *parent = 0);

    void dumpOSMs(const QString &baseFileName);

signals:

public slots:
    void strikePath(const VectorPath &path, const GraphicContext &context);
    void fillPath(const VectorPath &path, const GraphicContext &context, Qt::FillRule fillRule);
    void parsingDone(bool result);
private:
    void dumpOSM(const QString &fileName, QList<OSMPath> *paths, bool merge = false);

    QList<QPointF> convertToEPSG4326(const QList<QPointF> &points);

    QString m_projection;
    projPJ m_projection_source;
    projPJ m_projection_target;

    QRectF m_boundingBox, m_pdfBoundingBox;
    QPainterPath m_border;
    QList<OSMPath> m_houses;
    QList<OSMPath> m_waters;
    QList<OSMPath> m_rails;
    QList<OSMPath> m_cemeteries;
    QList<OSMPath> m_cityLimit;
    bool generateLands;
    QList<OSMPath> m_lands;
    QList<QColor> m_colors;
    QList<qreal> m_widths;

    // Used for cemetery detection
    QList<QPolygonF> m_closedPolygons;
    QList<QLineF> m_hLines, m_vLines;
    QList<QPointF> m_crosses;
    QList<QPointF> m_churches;

    // Used for church detection
    QList<QLineF> m_railLines;
};

#endif // OSMGENERATOR_H
